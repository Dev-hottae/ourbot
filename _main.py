import sys
import os
from urllib.parse import urlencode

from account import keys
from account.login import *
from scheduler_test.getData import *
from market_data.market_data import *
from apscheduler.schedulers.background import BackgroundScheduler

## 기본 변수설정
# account 관련변수
account_data = None

# 시장가격 데이터 호출 관련 변수
market = ["KRW-BTC", "KRW-ETH"]
current_price_url = "https://api.upbit.com/v1/ticker"
prev_price_url = "https://api.upbit.com/v1/candles/days"

global prev_btc_data
global prev_eth_data
global target_btc
global target_eth
money_for_btc = 0
money_for_eth = 0

# 매수가 결정을 위한 파라미터변수
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

    # 스케쥴러 등록
    sched = BackgroundScheduler()
    sched.start()

    ## 실제 실행
    # 9시 정각 모든 자산 매도주문 & 걸린 주문들 전체 취소
    # sched.add_job(request_sell, 'interval', seconds=100, id="sell_having_asset")
    # sched.add_job(waits_order_cancel, 'interval', seconds=100, id="order_cancel")



    # My account 정보 호출 // 잔고 변화 이벤트 있을 시 수시 호출 가능하게 변경할 것

    account_data = account_info()

    my_balance = account_data.json()[0].get('balance')
    my_balance = str(round(float(my_balance), 3))

    # 매매를 위한 금액설정
    money_for_btc = float(my_balance) * (49.5 / 100)
    money_for_eth = float(my_balance) * (49.5 / 100)

    main_currency = account_data.json()[0].get('currency')
    print("현재 My account Balance : " + my_balance + main_currency)


    # 시장 현재가 데이터 호출(쓰레드 분리)
    app = QApplication(sys.argv)
    # price_helper = Market_datas(market, current_price_url)
    # price_helper.finished.connect(price_helper.update_marketdata)
    # price_helper.start()


    # 스케쥴 테스트용
    sched.add_job(get_btc, 'interval', seconds=6, id="get_btc")
    sched.add_job(get_eth, 'interval', seconds=6, id="get_eth")
    sched.add_job(get_current_btc, 'interval', seconds=3, id="get_cur_btc")
    sched.add_job(get_current_eth, 'interval', seconds=3, id="get_cur_eth")

    while True:
        print("now running")
        time.sleep(5)

    # 스케쥴 매9시 실행
    # sched.add_job(get_btc, 'cron', hour=9, id="get_btc")
    # sched.add_job(get_eth, 'cron', hour=9, id="get_etc")

    # app.exec_()

    return

# 전일 데이터를 가져오기 위한 input data
get_url = "https://api.upbit.com/v1/candles/days"
querystring_BTC = {"market": "KRW-BTC", "count": "2", "convertingPriceUnit": "KRW"}
querystring_ETH = {"market": "KRW-ETH", "count": "2", "convertingPriceUnit": "KRW"}


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
    # if (sched.get_job("order_btc") != None):
    #     sched.remove_job('order_btc')

    response_krw = requests.request("GET", get_url, params=querystring_BTC)
    prev_data_json = response_krw.json()[1]
    # sched.add_job(order_btc, 'interval', seconds=1, id="order_btc")
    return prev_data_json


def get_eth():
    # if (sched.get_job("order_eht") != None):
    #     sched.remove_job('order_eth')
    response_krw = requests.request("GET", get_url, params=querystring_ETH)
    prev_data_json = response_krw.json()[1]
    # sched.add_job(order_eth, 'interval', seconds=1, id="order_eth")
    return prev_data_json


# 현재가 데이터를 가져오기위한 함수
def get_current_btc():
    url = "https://api.upbit.com/v1/ticker"
    querystring = {"markets": "KRW-BTC"}
    response = json.loads(requests.request("GET", url, params=querystring).text)
    global btc_trade_price
    btc_trade_price = response[0]["trade_price"]

    if btc_trade_price >= get_target_price_btc(get_btc()):
        order_btc()

    print("현재 btc 타겟 price : %s" %get_target_price_btc(get_btc()))
    print("currnet btc price : " + str(response[0]["trade_price"]))
    print("BTC 매수불가")
    return btc_trade_price

def get_current_eth():
    url = "https://api.upbit.com/v1/ticker"
    querystring = {"markets": "KRW-ETH"}
    response = json.loads(requests.request("GET", url, params=querystring).text)
    global eth_trade_price
    eth_trade_price = response[0]["trade_price"]

    if eth_trade_price >= get_target_price_eth(get_eth()):
        order_eth()

    print("현재 eth 타겟 price : %s" %get_target_price_eth(get_eth()))
    print("currnet eth price : " + str(response[0]["trade_price"]))
    print("ETH 매수불가")
    # return response


# 목표 매수가 돌파 시 주문 호출을 위한 함수
def order_btc():
    print('btc 주문실행...')
    access_key = keys.access_key
    secret_key = keys.secret_key
    server_url = 'https://api.upbit.com'
    global money_for_btc
    query = {
        'market': "KRW_BTC",
        'side': "bid",
        'volume': str(money_for_btc / get_target_price_btc(get_btc())),
        'price': str(get_target_price_btc(get_btc())),
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
    query = {
        'market': "KRW_ETH",
        'side': "bid",
        'volume': str(money_for_eth / get_target_price_eth(get_eth())),
        'price': str(get_target_price_eth(get_eth())),
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

# 오전9시 보유종목 매도 및 전체 등록 주문 취소
def sell_having_asset():

    pass

def waits_order_cancel():
    # 현재 대기열에 있는 주문들 uuid 값들을 가져옴
    wait_uuids = order_uuids("wait")
    if len(wait_uuids)==0:
        print("주문 취소할 waiting 이 없습니다...")
    print("총 %s 건의 주문이 waiting 중입니다...." % len(wait_uuids))

    for i in range(len(wait_uuids)):
        print("%s 번째 waiting 주문을 취소요청합니다..." %(i+1))
        order_cancel(wait_uuids[i])

    print("waiting 주문들의 취소가 완료되었습니다...")

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
        'state': situation,
    }
    query_string = urlencode(query)

    uuids_query_string = '&'.join(["uuids[]={}".format(uuid) for uuid in ordered_uuids])

    query['uuids[]'] = ordered_uuids
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
    done_uuids = order_uuids("done")
    if len(done_uuids)==0:
        print("현재 오전9시 매도할 자산이 없습니다...")
    print("총 %s 개의 자산을 보유하고 있습니다..." % len(done_uuids))

    for i in range(len(done_uuids)):
        print("%s 번째 자산 매도요청을 시작합니다..." %(i+1))
        sell_asset(done_uuids[i])

    print("모든 보유자산의 매도가 처리되었습니다....")


# 자산 처분 실행
def sell_asset(id):
    query = {
        'market': id['market'],
        'side': 'ask',
        'volume': id['volume'],
        'price': str(get_current_btc()),
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












