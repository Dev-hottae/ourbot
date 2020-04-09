# -*- coding: utf-8 -*-
import datetime
import time

from apscheduler.schedulers.background import BackgroundScheduler

from account import keys
from data_request import *
from order_request import *
from param_algo import *

## 기본 변수설정
# 손으로 수정해야하는 변수설정
global btc_min_unit
global eth_min_unit
global ub_trading_fee
global data_amount_for_param
global btc_money_rate
global eth_money_rate

btc_min_unit = 1000
eth_min_unit = 50
ub_trading_fee = 0.001
data_amount_for_param = 200     # 현재 200개가 max
btc_money_rate = 0.495
eth_money_rate = 0.495

# 기본 전역변수
global my_krw_balance
global prev_btc_data
global prev_eth_data
global target_btc
global target_eth

global money_for_btc
global money_for_eth
money_for_btc = 0
money_for_eth = 0

# 매수가 결정을 위한 파라미터변수
global parameter_btc
global parameter_eth
global parameter_bnb
parameter_btc = 1
parameter_eth = 1
parameter_bnb = 1

# 주문 완료 혹은 주문요청된 거래 uuid
total_ordered_uid = []

# 데이터 요청을 위한 기본 url
server_url = 'https://api.upbit.com'


def ub_Main():
    # 실행하면서 파라미터 세팅
    morning_9am()

    # 스케쥴러 등록
    sched = BackgroundScheduler()
    sched.start()

    # ## 실제 실행
    # # 9시 정각 모든 자산 매도주문 & 걸린 주문들 전체 취소 & 계좌데이터 refresh & 전일 데이터로 타겟 설정
    # gcp 는 00 시임
    sched.add_job(morning_9am, 'cron', hour=0, minute=0, second=1, id="morning_9am")

    # 프로그램 동작
    while True:
        global my_krw_balance

        global money_for_btc
        global money_for_eth

        try:
            btc_current_price = get_current_price("KRW-BTC")
            eth_current_price = get_current_price("KRW-ETH")

        except Exception as e:
            print("Error! :::::", e)

        else:
            if (btc_current_price >= target_btc) & (money_for_btc > 0):
                order_bid("KRW-BTC", target_btc, money_for_btc, btc_min_unit)

                # 매수 후 잔고 및 매수잔액 업데이트
                my_krw_balance = int(my_krw_balance) - int(money_for_btc)
                money_for_btc = 0

            if (eth_current_price >= target_eth) & (money_for_eth > 0):
                order_bid("KRW-ETH", target_eth, money_for_eth, eth_min_unit)

                # 매수 후 잔고 및 매수잔액 업데이트
                my_krw_balance = int(my_krw_balance) - int(money_for_eth)
                money_for_eth = 0

        time.sleep(1)


# 9시에 실행될 함수
def morning_9am():
    print("현재 시각 오전 9시@@@@")
    on_time = datetime.datetime.now().strftime('%Y-%m-%d' + 'T09:00:00')
    print(on_time)

    print("현재 주문 내역 : ", total_ordered_uid)
    request_sell()
    waits_order_cancel()

    total_ordered_uid.clear()
    print("-----전일 주문 취소 완료!!-----")

    account_data = account_info()

    global my_krw_balance
    my_krw_account_data = []
    for i in range(len(account_data)):
        if account_data[i]['currency'] == 'KRW':
            my_krw_account_data.append(account_data[i])
            break

    my_krw_balance = my_krw_account_data[0].get('balance')
    my_krw_balance = int(float(my_krw_balance))

    # 매매를 위한 금액설정
    global money_for_btc
    global money_for_eth
    money_for_btc = float(my_krw_balance) * btc_money_rate
    money_for_eth = float(my_krw_balance) * eth_money_rate

    main_currency = my_krw_account_data[0].get('currency')
    print("금일 현재 My account Balance : ", my_krw_balance, main_currency)

    print("-----금일 계좌 데이터 초기화 완료!!!-----")

    ## 200 전 데이터 요청
    btc_data_200 = get_day_candle("KRW-BTC", data_amount_for_param)
    eth_data_200 = get_day_candle("KRW-ETH", data_amount_for_param)

    ## 파라미터 계산
    global parameter_btc
    global parameter_eth
    parameter_btc = william_param(btc_data_200, ub_trading_fee)
    print("btc 최적파라미터 : ", parameter_btc)
    parameter_eth = william_param(eth_data_200, ub_trading_fee)
    print("eth 최적파라미터 : ", parameter_eth)

    print("----- 파라미터 수정 완료!! -----")

    global target_btc
    global target_eth
    target_btc = target_price(get_day_candle("KRW-BTC", 2)[1], parameter_btc)
    target_eth = target_price(get_day_candle("KRW-ETH", 2)[1], parameter_eth)
    print("금일 BTC target Price : ", target_btc)
    print("금일 ETH target Price : ", target_eth)
    print("-----target price 설정 완료!!-----")


# 오전9시 보유종목 매도 및 전체 등록 주문 취소
def waits_order_cancel():
    # 현재 대기열에 있는 주문들 uuid 값들을 가져옴
    wait_uuids = uuids_by_state('wait', total_ordered_uid)
    print("대기중인 uuid : ", wait_uuids)
    if len(wait_uuids) == 0:
        print("현재 waiting 주문의 건이 없습니다...")
        return
    print("총 %s 건의 주문이 waiting 중입니다...." % len(wait_uuids))
    for i in range(len(wait_uuids)):
        order_cancel(wait_uuids[i])
        print("처리된 uuid : ", wait_uuids[i])
    print("waiting 주문들의 취소가 정상 처리되었습니다...")


# 오전 9시 현재 보유자산 처분 요청
def request_sell():
    # 현재 주문 완료된 uuid 값들을 가져옴
    done_uuids = uuids_by_state('done', total_ordered_uid)
    print("매도해야할 uuid: ", done_uuids)
    if len(done_uuids) == 0:
        print("현재 매수완료된 주문의 건이 없습니다...")
        return
    print("총 %s 개의 자산을 보유하고 있습니다..." % len(done_uuids))

    for i in range(len(done_uuids)):
        sell_asset(done_uuids[i])
        print("처리된 uuid : ", done_uuids[i])
    print("모든 보유자산의 매도가 정상 처리되었습니다....")
