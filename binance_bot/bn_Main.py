
from apscheduler.schedulers.background import BackgroundScheduler

from account.keys import *
from binance_bot.bn_Client import *

# 메세징 봇
global tg_bot

# 로그인 완료
global bn_client


def bn_main(tg):
    global bn_client
    bn_client = Bn_Client(bn_access_key, bn_secret_key)

    # 텔레그램 봇 세팅
    global tg_bot
    tg_bot = tg

    # 실행하면서 파라미터 초기화
    initializer()

    # 스케쥴러 등록
    sched = BackgroundScheduler()
    sched.start()

    ## 실제 실행
    # 9시 정각 모든 자산 매도주문 & 걸린 주문들 전체 취소 & 계좌데이터 refresh & 전일 데이터로 타겟 설정
    # gcp 는 00 시임
    sched.add_job(initializer, 'cron', hour=1, minute=36, second=20, id="initializer")
    while True:
        # 현재시각 : 살아있는지 확인용
        on_time = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S %Z%z')
        print(on_time)
        time.sleep(3600)


def initializer():
    print("현재 시각 오전 9시@@@@")
    on_time = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S %Z%z')
    print(on_time)

    print("어제자 주문 내역 : " + str(bn_client.total_ordered_uid))

    # 어제 주문내역 옮김
    bn_client.yesterday_uid = bn_client.total_ordered_uid[:]

    # 전일 주문 청산 및 취소 진행
    for i in range(len(bn_client.total_ordered_uid)):
        order_info = bn_client.query_order(bn_client.total_ordered_uid[i][0], bn_client.total_ordered_uid[i][1])
        if order_info["status"] == "NEW":
            bn_client.cancel_order(order_info["symbol"], order_info["orderId"])

        elif order_info["status"] == "FILLED ":
            bn_client.new_order_market(order_info["symbol"], "SELL", "MARKET", order_info["executedQty"])

        else:
            pass

    bn_client.total_ordered_uid.clear()
    print("-----전일 주문 취소 완료!!-----")

    # 잔고 초기화
    balance_all = bn_client.account_info()

    for i in range(len(balance_all)):
        if balance_all[i]["asset"] == "USDT":
            bn_client.my_rest_balance = int(float(balance_all[i]["free"]))
            break

    print("금일 현재 My account Balance : " + str(bn_client.my_rest_balance) + " USDT")
    print("-----금일 계좌 데이터 초기화 완료!!!-----")

    # 매매를 위한 금액설정
    bn_client.W1_btc_money = int(bn_client.my_rest_balance * bn_client.W1_btc_rate)
    bn_client.W1_eth_money = int(bn_client.my_rest_balance * bn_client.W1_eth_rate)
    bn_client.W1_bnb_money = int(bn_client.my_rest_balance * bn_client.W1_bnb_rate)
    print(bn_client.W1_bnb_money)

    # 과거 데이터 요청
    prev_btc_data = bn_client.prev_data_request("BTCUSDT", bn_client.W1_data_amount_for_param)
    prev_eth_data = bn_client.prev_data_request("ETHUSDT", bn_client.W1_data_amount_for_param)
    prev_bnb_data = bn_client.prev_data_request("BNBUSDT", bn_client.W1_data_amount_for_param)

    # 파라미터 계산
    parameter_btc = william_param(prev_btc_data, Bn_Client.BN_FEE)
    print("btc 최적파라미터 : " + str(parameter_btc))
    parameter_eth = william_param(prev_eth_data, Bn_Client.BN_FEE)
    print("eth 최적파라미터 : " + str(parameter_eth))
    parameter_bnb = william_param(prev_bnb_data, Bn_Client.BN_FEE)
    print("bnb 최적파라미터 : " + str(parameter_bnb))

    print("----- 파라미터 수정 완료!! -----")

    # 타겟 가격 설정
    btc_target_price = round(target_price(bn_client.prev_data_request("BTCUSDT", 2)[1], parameter_btc), 2)
    eth_target_price = round(target_price(bn_client.prev_data_request("ETHUSDT", 2)[1], parameter_eth), 2)
    bnb_target_price = round(target_price(bn_client.prev_data_request("BNBUSDT", 2)[1], parameter_bnb), 4)

    # 주문량 결정
    ava_btc_amount = round((bn_client.W1_btc_money / btc_target_price), 6)
    ava_eth_amount = round((bn_client.W1_eth_money / eth_target_price), 5)
    ava_bnb_amount = round((bn_client.W1_bnb_money / bnb_target_price), 2)

    # 스탑리밋 주문 실행
    try:
        btc_stoplimit = bn_client.new_order_stoplimit("BTCUSDT", "BUY", "STOP_LOSS_LIMIT", "GTC", ava_btc_amount, btc_target_price,
                                                      btc_target_price)
    except Exception as e:
        bn_client.print_put("BTC 스탑리밋 주문 에러발생!!!")
        btc_limitorder = bn_client.new_order_limit("BTCUSDT", "BUY", "LIMIT", "GTC", ava_btc_amount, btc_target_price)
        tg_bot.sendMessage(chat_id=tg_my_id, text="<BN> BTC 지정가 주문 실행!!!")

    try:
        eth_stoplimit = bn_client.new_order_stoplimit("ETHUSDT", "BUY", "STOP_LOSS_LIMIT", "GTC", ava_eth_amount, eth_target_price,
                                                  eth_target_price)
    except Exception as e:
        bn_client.print_put("ETH 스탑리밋 주문 에러발생!!!")
        btc_limitorder = bn_client.new_order_limit("ETHUSDT", "BUY", "LIMIT", "GTC", ava_eth_amount, eth_target_price)
        tg_bot.sendMessage(chat_id=tg_my_id, text="<BN> ETH 지정가 주문 실행!!!")

    try:
        bnb_stoplimit = bn_client.new_order_stoplimit("BNBUSDT", "BUY", "STOP_LOSS_LIMIT", "GTC", ava_bnb_amount, bnb_target_price,
                                                  bnb_target_price)
    except Exception as e:
        bn_client.print_put("BNB 스탑리밋 주문 에러발생!!!")
        btc_limitorder = bn_client.new_order_limit("BNBUSDT", "BUY", "LIMIT", "GTC", ava_bnb_amount, bnb_target_price)
        tg_bot.sendMessage(chat_id=tg_my_id, text="<BN> BNB 지정가 주문 실행!!!")

    bn_client.print_put("----- 타겟가격, 주문량 수정 후 스탑리밋 주문 요청 완료!! -----")
    bn_client.print_put("오늘자로 주문된 주문 id : " + str(bn_client.total_ordered_uid))

    # 금일자 최신화 정보
    alert_data = {
        "time": on_time,
        "yesterday_order": bn_client.yesterday_uid,
        "today_uid": bn_client.total_ordered_uid,
        "Balance": str(bn_client.my_rest_balance) + " USDT",
        "parameter_btc": parameter_btc,
        "parameter_eth": parameter_eth,
        "parameter_bnb": parameter_bnb,
        "target_btc": str(btc_target_price) + " USDT",
        "target_eth": str(eth_target_price) + " USDT",
        "target_bnb": str(bnb_target_price) + " USDT"
    }

    # 9시 최신화 정보 telegram 알림
    msg = msg_reorg(alert_data)
    tg_bot.sendMessage(chat_id=tg_my_id, text=msg)

    # bn_client.all_print()


# 메세징 재정리 함수
def msg_reorg(data):
    msg = "--바이낸스 봇 알림!--\n"
    key_list = list(data.keys())
    for i in range(len(data)):
        msg += key_list[i]
        msg += " : "
        msg += str(data[str(key_list[i])])
        msg += "\n"

    return msg
