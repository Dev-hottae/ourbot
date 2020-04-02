# -*- coding: utf-8 -*-
import hashlib
import json
import time
import uuid
from urllib.parse import urlencode
from param_algo import *
import jwt
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from account import keys

## 기본 변수설정
# account 관련변수
account_data = None

# 시장가격 데이터 호출 관련 변수
market = ["KRW-BTC", "KRW-ETH"]
current_price_url = "https://api.upbit.com/v1/ticker"
prev_price_url = "https://api.upbit.com/v1/candles/days"

# 전일 데이터를 가져오기 위한 input data
get_url = "https://api.upbit.com/v1/candles/days"
querystring_BTC = {"market": "KRW-BTC", "count": "2", "convertingPriceUnit": "KRW"}
querystring_ETH = {"market": "KRW-ETH", "count": "2", "convertingPriceUnit": "KRW"}

global my_balance
global prev_btc_data
global prev_eth_data
global target_btc
global target_eth
global btc_current_price
btc_current_price = 0
global eth_current_price
eth_current_price = 0
money_for_btc = 0
money_for_eth = 0

# 매수가 결정을 위한 파라미터변수
global parameter_btc
global parameter_eth
global parameter_bnb
parameter_btc = 0.57
parameter_eth = 0.7
parameter_bnb = 0.5

# 주문 완료 혹은 주문요청된 거래 uuid
ordered_uuids = []

# 데이터 요청을 위한 기본 변수
access_key = keys.access_key
secret_key = keys.secret_key
server_url = 'https://api.upbit.com'

def Main():
    # 실행하면서 파라미터 세팅
    morning_9am()

    # 스케쥴러 등록
    sched = BackgroundScheduler()
    sched.start()

    # 테스트 오더
    # order_btc_for_waiting()
    # print("대기용 매수주문완료")
    # order_btc_for_done()
    # print("매도용 매수주문완료")

    # ## 실제 실행
    # # 9시 정각 모든 자산 매도주문 & 걸린 주문들 전체 취소 & 계좌데이터 refresh & 전일 데이터로 타겟 설정
    sched.add_job(morning_9am, 'cron', hour=9, id="morning_9am")

    # # 현재 데이터 지속적으로 받아오기
    sched.add_job(get_current_btc, 'interval', seconds=2, id="get_cur_btc")
    sched.add_job(get_current_eth, 'interval', seconds=2, id="get_cur_eth")

    while True:
        # print("now running")
        global btc_current_price
        global eth_current_price

        global my_balance

        global money_for_btc
        global money_for_eth

        # print("btc 현재가 : ", btc_current_price)
        # print("eth 현재가 : ", eth_current_price)
        if ((btc_current_price >= get_target_price_btc(get_btc())) & (money_for_btc > 0)):
            order_btc()

            # 매수 후 잔고 및 매수잔액 업데이트
            my_balance = my_balance - money_for_btc
            money_for_btc = 0

        if ((eth_current_price >= get_target_price_eth(get_eth())) & (money_for_eth > 0)):
            order_eth()

            # 매수 후 잔고 및 매수잔액 업데이트
            my_balance = my_balance - money_for_eth
            money_for_eth = 0

        time.sleep(1)
    return


# 9시에 실행될 함수
def morning_9am():
    print("현재 시각 오전 9시@@@@")
    print("현재 주문 내역 : ", ordered_uuids)
    request_sell()
    waits_order_cancel()

    ordered_uuids.clear()
    print("-----전일 주문 취소 완료!!-----")

    account_data = account_info()

    global my_balance
    my_balance = account_data.json()[0].get('balance')
    my_balance = str(int(float(my_balance)))

    # 매매를 위한 금액설정
    global money_for_btc
    global money_for_eth
    money_for_btc = float(my_balance) * (49.5 / 100)
    money_for_eth = float(my_balance) * (49.5 / 100)

    main_currency = account_data.json()[0].get('currency')
    print("금일 현재 My account Balance : " + my_balance + main_currency)

    print("-----금일 계좌 데이터 초기화 완료!!!-----")

    get_btc()
    get_eth()

    print("-----전일 데이터 요청 완료!!-----")

    ## 200 전 데이터 요청
    btc_data_200 = get_day_candle("KRW-BTC", 200)
    eth_data_200 = get_day_candle("KRW-ETH", 200)

    ## 파라미터 계산
    global parameter_btc
    global parameter_eth
    parameter_btc = param(btc_data_200)
    print("btc 최적파라미터 : ", parameter_btc)
    parameter_eth = param(eth_data_200)
    print("eth 최적파라미터 : ", parameter_eth)

    print("----- 파라미터 수정 완료!! -----")

# 계정 데이터 관련 함수
def account_info():
    access_key = keys.access_key
    secret_key = keys.secret_key
    server_url = 'https://api.upbit.com'

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    res = requests.get(server_url + "/v1/accounts", headers=headers)
    return res

# 전일 데이터 호출함수
def get_btc():
    # querystring = {"market": "KRW-ETH", "count": "3"}
    querystring_BTC = {"market": "KRW-BTC", "count": "2", "convertingPriceUnit": "KRW"}
    response_krw = requests.request("GET", get_url, params=querystring_BTC)
    prev_data_json = response_krw.json()[1]
    return prev_data_json

#### 일단위 캔들요청 수정본
def get_day_candle(market, count):
    querystring = {"market": str(market), "count": str(count), "convertingPriceUnit": "KRW"}
    response_krw = requests.request("GET", get_url, params=querystring)
    prev_data_json = response_krw.json()
    return prev_data_json

def get_eth():
    response_krw = requests.request("GET", get_url, params=querystring_ETH)
    prev_data_json = response_krw.json()[1]
    return prev_data_json


# 현재가 데이터를 가져오기위한 함수
def get_current_btc():
    url = "https://api.upbit.com/v1/ticker"
    querystring = {"markets": "KRW-BTC"}
    response = json.loads(requests.request("GET", url, params=querystring).text)
    global btc_current_price
    btc_current_price = response[0]["trade_price"]
    print("BTC 현재가 : ", btc_current_price)
    return btc_current_price

def get_current_eth():
    url = "https://api.upbit.com/v1/ticker"
    querystring = {"markets": "KRW-ETH"}
    response = json.loads(requests.request("GET", url, params=querystring).text)
    global eth_current_price
    eth_current_price = response[0]["trade_price"]
    print("ETH 현재가 : ", eth_current_price)
    return eth_current_price


# 목표 매수가 돌파 시 주문 호출을 위한 함수
def order_btc():
    print('btc 주문실행...')
    access_key = keys.access_key
    secret_key = keys.secret_key
    server_url = 'https://api.upbit.com'
    global money_for_btc
    volume = "{0:.8f}".format(money_for_btc / get_target_price_btc(get_btc()))
    price = int((get_target_price_btc(get_btc())//1000)*1000)
    query = {
        'market': "KRW-BTC",
        'side': "bid",
        'volume': str(volume),
        'price': str(price),
        'ord_type': "limit",
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    res = res.json()
    # 주문 날리면 uuid 저장
    ordered_uuids.append(res["uuid"])


def order_eth():
    print('eth 주문실행...')
    access_key = keys.access_key
    secret_key = keys.secret_key
    server_url = 'https://api.upbit.com'
    global money_for_eth
    volume = "{0:.8f}".format(money_for_eth / get_target_price_eth(get_eth()))
    price = int((get_target_price_eth(get_eth()) // 50) * 50)
    query = {
        'market': "KRW-ETH",
        'side': "bid",
        'volume': str(volume),
        'price': str(price),
        'ord_type': "limit",
    }

    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    res = res.json()

    # 주문 날리면 uuid 저장
    ordered_uuids.append(res["uuid"])

# 매수가 결정함수
def get_target_price_btc(coin_price):
    target_price = 0
    open = int(coin_price["opening_price"])
    close = int(coin_price["trade_price"])
    high = int(coin_price["high_price"])
    low = int(coin_price["low_price"])

    target_price = open + (high - low) * parameter_btc

    return target_price

def get_target_price_eth(coin_price):
    target_price = 0
    open = int(coin_price["opening_price"])
    close = int(coin_price["trade_price"])
    high = int(coin_price["high_price"])
    low = int(coin_price["low_price"])

    target_price = open + (high - low) * parameter_eth

    return target_price

### 오전9시 보유종목 매도 및 전체 등록 주문 취소
def waits_order_cancel():
    # 현재 대기열에 있는 주문들 uuid 값들을 가져옴
    wait_uuids = order_uuids('wait')
    print("대기중인 uuid : ", wait_uuids)
    if len(wait_uuids)==0:
        print("현재 waiting 주문의 건이 없습니다...")
        return
    print("총 %s 건의 주문이 waiting 중입니다...." % len(wait_uuids))
    for i in range(len(wait_uuids)):
        order_cancel(wait_uuids[i])
        # ordered_uuids.remove(wait_uuids[i])  # 취소 후 uuid 제거
    print("waiting 주문들의 취소가 정상 처리되었습니다...")

def order_cancel(id):
    query = {
        'uuid': id["uuid"],
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': keys.access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, keys.secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.delete(server_url + "/v1/order", params=query, headers=headers)

# 현재 대기열에 있는 주문 uuid 값들을 가져옴
def order_uuids(situation):
    query = {
        'state': situation
    }
    query_string = urlencode(query)

    uuids_query_string = '&'.join(["uuids[]={}".format(uuid) for uuid in ordered_uuids])
    query['uuids[]'] = ordered_uuids
    if (len(query['uuids[]'])) == 0 :
        return []

    else :
        query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(server_url + "/v1/orders", params=query, headers=headers)
        return res.json()



# 오전 9시 현재 보유자산 처분 요청
def request_sell():
    # 현재 주문 완료된 uuid 값들을 가져옴
    done_uuids = order_uuids('done')
    print("매도해야할 uuid: ", done_uuids)
    if len(done_uuids)==0:
        print("현재 매수완료된 주문의 건이 없습니다...")
        return
    print("총 %s 개의 자산을 보유하고 있습니다..." % len(done_uuids))

    for i in range(len(done_uuids)):
        sell_asset(done_uuids[i])
        # ordered_uuids.remove(done_uuids[i])     # 매도 후 uuid 제거
    print("모든 보유자산의 매도가 정상 처리되었습니다....")


# 자산 처분 실행
def sell_asset(id):
    query = {
        'market': id['market'],
        'side': 'ask',
        'volume': id['volume'],
        'ord_type': 'market',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)








### 테스트용 오더

def order_btc_for_waiting():
    print('btc 주문실행...')
    access_key = keys.access_key
    secret_key = keys.secret_key
    server_url = 'https://api.upbit.com'

    query = {
        'market': 'KRW-BTC',
        'side': 'bid',
        'volume': '0.00015714',
        'price': '7000000',
        'ord_type': 'limit',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    res = res.json()
    time.sleep(3)
    print("uuid 찾기 위한 프린트 : ", res)
    ordered_uuids.append(res["uuid"])



def order_btc_for_done():
    print('btc 주문실행...')
    access_key = keys.access_key
    secret_key = keys.secret_key
    server_url = 'https://api.upbit.com'

    query = {
        'market': 'KRW-BTC',
        'side': 'bid',
        'volume': '0.00013415',
        'price': '8300000',
        'ord_type': 'limit',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    res = res.json()
    time.sleep(3)
    print("uuid 찾기 위한 프린트 : ", res)
    ordered_uuids.append(res["uuid"])

