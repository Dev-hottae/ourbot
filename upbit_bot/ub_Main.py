import datetime
import time

from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

from algoset.larry_williams import *
from upbit_bot.ub_Client import *

# 메세징 봇
global tg_bot

# 로그인 완료
global ub_client

# 매수 타겟 가격
global target_btc
global target_eth


def ub_main(tg):
    global ub_client
    ub_client = Ub_Client(ub_access_key, ub_secret_key)

    # 텔레그램 봇 세팅
    global tg_bot
    tg_bot = tg

    # 실행하면서 파라미터 세팅
    initializer()

    # 스케쥴러 등록
    sched = BackgroundScheduler()
    sched.start()

    ## 실제 실행
    # 9시 정각 모든 자산 매도주문 & 걸린 주문들 전체 취소 & 계좌데이터 refresh & 전일 데이터로 타겟 설정
    # gcp 는 00 시임
    sched.add_job(initializer, 'cron', hour=0, minute=0, second=1, id="initializer")

    while True:

        try:
            # 현재가 받아오기
            btc_current_price = json.loads(ub_client.get_current_price("KRW-BTC"))[0]["trade_price"]
            eth_current_price = json.loads(ub_client.get_current_price("KRW-ETH"))[0]["trade_price"]
            print("현재 %s 가격 : " % "KRW-BTC", btc_current_price)
            print("현재 %s 가격 : " % "KRW-ETH", eth_current_price)

        except Exception as e:
            print("Error! :::::", e)


        else:
            # 받아온 현재가 조건 체크
            if (btc_current_price >= target_btc) & (ub_client.W1_btc_money > 0):
                order_uuid = ub_client.order_bid_market("KRW-BTC", ub_client.W1_btc_money)
                ub_client.total_ordered_uid.append(order_uuid)

                # 매수 후 잔고 및 매수잔액 업데이트
                ub_client.my_krw_balance = int(ub_client.my_krw_balance) - int(ub_client.W1_btc_money)
                ub_client.W1_btc_money = 0

                tg_bot.sendMessage(chat_id=tg_my_id, text="BTC 시장가주문 요청합니다...")

            if (eth_current_price >= target_eth) & (ub_client.W1_eth_money > 0):
                order_uuid = ub_client.order_bid_market("KRW-ETH", ub_client.W1_eth_money)
                ub_client.total_ordered_uid.append(order_uuid)

                # 매수 후 잔고 및 매수잔액 업데이트
                ub_client.my_krw_balance = int(ub_client.my_krw_balance) - int(ub_client.W1_eth_money)
                ub_client.W1_eth_money = 0

                tg_bot.sendMessage(chat_id=tg_my_id, text="ETH 시장가주문 요청합니다...")

        time.sleep(1)


def initializer():
    print("현재 시각 오전 9시@@@@")
    on_time = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S %Z%z')
    print(on_time)

    print("현재 주문 내역 : ", ub_client.total_ordered_uid)
    ub_client.request_sell()
    ub_client.waits_order_cancel()

    ub_client.total_ordered_uid.clear()
    print("-----전일 주문 취소 완료!!-----")

    account_data = ub_client.account_info()

    my_krw_account_data = []
    for i in range(len(account_data)):
        if account_data[i]['currency'] == 'KRW':
            my_krw_account_data.append(account_data[i])
            break

    ub_client.my_krw_balance = int(float(my_krw_account_data[0].get('balance')))

    # 매매를 위한 금액설정
    ub_client.W1_btc_money = float(ub_client.my_krw_balance) * ub_client.W1_btc_rate
    ub_client.W1_eth_money = float(ub_client.my_krw_balance) * ub_client.W1_eth_rate

    main_currency = my_krw_account_data[0].get('currency')
    print("금일 현재 My account Balance : ", ub_client.my_krw_balance, main_currency)

    print("-----금일 계좌 데이터 초기화 완료!!!-----")

    ## 200 전 데이터 요청
    btc_data_200 = ub_client.get_day_candle("KRW-BTC", ub_client.W1_data_amount_for_param)
    eth_data_200 = ub_client.get_day_candle("KRW-ETH", ub_client.W1_data_amount_for_param)

    ## 파라미터 계산
    parameter_btc = william_param(btc_data_200, Ub_Client.TR_FEE)
    print("btc 최적파라미터 : ", parameter_btc)
    parameter_eth = william_param(eth_data_200, Ub_Client.TR_FEE)
    print("eth 최적파라미터 : ", parameter_eth)

    print("----- 파라미터 수정 완료!! -----")
    
    # 타겟 가격 설정
    global target_btc
    global target_eth
    target_btc = target_price(ub_client.get_day_candle("KRW-BTC", 2)[1], parameter_btc)
    target_eth = target_price(ub_client.get_day_candle("KRW-ETH", 2)[1], parameter_eth)
    print("금일 BTC target Price : ", target_btc)
    print("금일 ETH target Price : ", target_eth)
    print("-----target price 설정 완료!!-----")

    # 금일자 최신화 정보
    alert_data = {
        "time": on_time,
        "total_ordered_uid": ub_client.total_ordered_uid,
        "Balance": str(ub_client.my_krw_balance) + " KRW",
        "parameter_btc": parameter_btc,
        "parameter_eth": parameter_eth,
        "target_btc": target_btc,
        "target_eth": target_eth
    }

    # 9시 최신화 정보 telegram 알림
    msg = msg_reorg(alert_data)
    tg_bot.sendMessage(chat_id=tg_my_id, text=msg)

# 기간 수익률 구하는 함수
def profit_rate():
    pass




# 메세징 재정리 함수
def msg_reorg(data):
    msg = "--업비트 봇 알림!--\n"
    key_list = list(data.keys())
    for i in range(len(data)):
        msg += key_list[i]
        msg += " : "
        msg += str(data[str(key_list[i])])
        msg += "\n"

    return msg
