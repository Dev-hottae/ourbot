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

# 파라미터 작업 중 잠시 stop 을 위한 파라미터
global stop_trading
stop_trading = True


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
    sched.add_job(initializer, 'cron', hour=0, minute=0, second=0, id="initializer")

    while True:

        # 파라미터 작업중에는 동작하지 않도록 설정
        if stop_trading == False:
            try:
                # 현재가 받아오기
                btc_current_price = json.loads(ub_client.get_current_price("KRW-BTC"))[0]["trade_price"]
                eth_current_price = json.loads(ub_client.get_current_price("KRW-ETH"))[0]["trade_price"]
                # print("현재 %s 가격 : " % "KRW-BTC", btc_current_price)
                # print("현재 %s 가격 : " % "KRW-ETH", eth_current_price)

            except Exception as e:
                print("Error! :::::", e)


            else:
                # 받아온 현재가 조건 체크
                if (btc_current_price >= target_btc) & (ub_client.W1_btc_money > 0):
                    order_info = ub_client.order_bid_market("KRW-BTC", ub_client.W1_btc_money)
                    ub_client.total_ordered_uid.append(order_info)

                    # 매수 후 잔고 및 매수잔액 업데이트
                    ub_client.my_krw_balance = int(ub_client.my_krw_balance) - int(ub_client.W1_btc_money)
                    ub_client.W1_btc_money = 0

                    tg_bot.sendMessage(chat_id=tg_my_id, text="<UB> BTC 시장가주문 요청합니다...")

                if (eth_current_price >= target_eth) & (ub_client.W1_eth_money > 0):
                    order_info = ub_client.order_bid_market("KRW-ETH", ub_client.W1_eth_money)
                    ub_client.total_ordered_uid.append(order_info)

                    # 매수 후 잔고 및 매수잔액 업데이트
                    ub_client.my_krw_balance = int(ub_client.my_krw_balance) - int(ub_client.W1_eth_money)
                    ub_client.W1_eth_money = 0

                    tg_bot.sendMessage(chat_id=tg_my_id, text="<UB> ETH 시장가주문 요청합니다...")

        time.sleep(1)


def initializer():
    # 매매 멈춤
    global stop_trading
    stop_trading = True

    print("현재 시각 오전 9시@@@@")
    on_time = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S %Z%z')
    print(str(on_time))

    # 전일 주문 상태 갱신
    ub_client.yesterday_uid.clear()
    for i in range(len(ub_client.total_ordered_uid)):
        uid = ub_client.indiv_order(ub_client.total_ordered_uid['uuid'])
        ub_client.yesterday_uid.append(uid)

    print("어제자 주문 내역 : " + str(ub_client.yesterday_uid))

    # 어제자 자산 매도 주문 실행
    for i in range(len(ub_client.yesterday_uid)):
        ub_client.order_ask_market(ub_client.yesterday_uid[i])

    ub_client.total_ordered_uid.clear()
    print("-----전일 주문 취소 완료!!-----")

    ## 200 전 데이터 요청
    btc_data_200 = ub_client.get_day_candle("KRW-BTC", ub_client.W1_data_amount_for_param)
    eth_data_200 = ub_client.get_day_candle("KRW-ETH", ub_client.W1_data_amount_for_param)

    ## 파라미터 계산
    parameter_btc = william_param(btc_data_200, Ub_Client.TR_FEE)
    print("btc 최적파라미터 : " + str(parameter_btc))
    parameter_eth = william_param(eth_data_200, Ub_Client.TR_FEE)
    print("eth 최적파라미터 : " + str(parameter_eth))

    print("----- 파라미터 수정 완료!! -----")

    # 타겟 가격 설정
    global target_btc
    global target_eth
    target_btc = int(target_price(ub_client.get_day_candle("KRW-BTC", 2)[1], parameter_btc))
    target_eth = int(target_price(ub_client.get_day_candle("KRW-ETH", 2)[1], parameter_eth))
    print("금일 BTC target Price : " + str(target_btc))
    print("금일 ETH target Price : " + str(target_eth))
    print("-----target price 설정 완료!!-----")

    # 계좌 및 잔액 관련 업데이트
    ## 주문 직후 잔액이 바로 업데이트가 되지는 않음 해결책 필요함 일단은 가장 이후에 작업하도록 맨 뒤로 옮김
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
    print("금일 현재 My account Balance : " + str(ub_client.my_krw_balance) + str(main_currency))

    print("-----금일 계좌 데이터 및 매수예정금 초기화 완료!!!-----")

    # 금일자 최신화 정보
    alert_data = {
        "time": on_time,
        "yesterday_order": ub_client.yesterday_uid,
        "from_now_uid": ub_client.total_ordered_uid,
        "Balance": str(ub_client.my_krw_balance) + " KRW",
        "parameter_btc": parameter_btc,
        "parameter_eth": parameter_eth,
        "target_btc": str(target_btc) + " KRW",
        "target_eth": str(target_eth) + " KRW"
    }

    # 9시 최신화 정보 telegram 알림
    msg = msg_reorg(alert_data)
    tg_bot.sendMessage(chat_id=tg_my_id, text=msg)

    # ub_client.all_print()

    # 매매 다시 시작
    stop_trading = False


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


def stop_for_while():
    pass
