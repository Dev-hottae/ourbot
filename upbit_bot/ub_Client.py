import datetime
import hashlib
import json
import time
import uuid
from urllib.parse import urlencode

import jwt
import requests
from pytz import timezone

from account.keys import *


class Ub_Client():
    HOST = 'https://api.upbit.com'

    TR_FEE = 0.002

    BTC_MIN_UNIT = 1000
    ETH_MIN_UNIT = 50



    def __init__(self, api_key, sec_key):
        self.A_key = api_key
        self.S_key = sec_key


        self.account_data = self.account_info()
        
        # 주문 정보
        self.yesterday_uid = []
        self.total_ordered_uid = []

        # 전체 콘솔 프린트
        self.total_print = []

        # 계좌 잔고
        my_krw_account_data = []
        for i in range(len(self.account_data)):
            if self.account_data[i]['currency'] == 'KRW':
                my_krw_account_data.append(self.account_data[i])
                break

        # 현재 보유 원화잔고
        self.my_krw_balance = int(float(my_krw_account_data[0].get('balance')))

        # william 알고리즘 위한 금액 세팅
        self.W1_btc_money = 0
        self.W1_eth_money = 0
        self.W1_btc_rate = 0.49
        self.W1_eth_rate = 0.49

        self.W1_data_amount_for_param = 200 # max limit 이 200개


    # 현재 계정 데이터 요청
    def account_info(self):
        endpoint = "/v1/accounts"

        payload = {
            'access_key': self.A_key,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, self.S_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        url = Ub_Client.HOST + endpoint

        res = requests.get(url, headers=headers)
        return res.json()


    #### 일단위 캔들요청 수정본
    def get_day_candle(self, market, count):
        endpoint = "/v1/candles/days"
        querystring = {"market": str(market), "count": str(count), "convertingPriceUnit": "KRW"}

        on_time = datetime.datetime.now(timezone('UTC')).strftime('%Y-%m-%d')

        # utc 시간 기준으로 올바른 데이터가 다 넘어왔을 때 리턴
        response_krw = requests.get(Ub_Client.HOST + endpoint, params=querystring)
        prev_data_json = response_krw.json()

        timer = 0
        while (on_time not in prev_data_json[0]["candle_date_time_utc"]) | (timer == 10):
            response_krw = requests.get(Ub_Client.HOST + endpoint, params=querystring)
            prev_data_json = response_krw.json()
            timer += 1
            time.sleep(1)
        else:
            return prev_data_json


    # 현재가 데이터를 가져오기 위한 함수 // not websocket
    def get_current_price(self, market):
        endpoint = "/v1/ticker"
        querystring = {"markets": market}

        url = Ub_Client.HOST + endpoint

        response = requests.request("GET", url, params=querystring)
        return response.text

    # 시장가 매도주문 호출을 위한 함수
    def order_ask_market(self, id):
        query = {
            'market': id['market'],
            'side': 'ask',
            'volume': id['executed_volume'],
            'ord_type': 'market',
        }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': ub_access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, ub_secret_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.post(Ub_Client.HOST + "/v1/orders", params=query, headers=headers)
        return res.json()

    # 시장가 매수주문 호출을 위한 함수
    def order_bid_market(self, market, total_price):
        print(market, '주문실행...')
        query = {
            'market': market,
            'side': "bid",
            'price': str(total_price),
            'ord_type': "price"
        }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.A_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.S_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.post(Ub_Client.HOST + "/v1/orders", params=query, headers=headers)

        # 주문 날리면 info 리턴
        return res.json()

    # 개별 주문 조회
    def indiv_order(self, id):
        query = {
            'uuid': id,
        }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.A_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.S_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(Ub_Client.HOST + "/v1/order", params=query, headers=headers)

        return res.json()

    # 현재 대기열에 있는 주문 uuid 들의 값들을 가져옴
    def uuids_by_state(self, situation, ordered_uuids):
        query = {
            'state': situation,
        }
        query_string = urlencode(query)

        uuids = ordered_uuids
        uuids_query_string = '&'.join(["uuids[]={}".format(_uuid) for _uuid in uuids])

        query['uuids[]'] = uuids
        if len(query['uuids[]']) == 0:
            return []

        query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.A_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.S_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(Ub_Client.HOST + "/v1/orders", params=query, headers=headers)

        return res.json()

    ## uuid 기반 기주문 취소 요청
    def order_cancel(self, id):
        query = {
            'uuid': id["uuid"],
        }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': ub_access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, ub_secret_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.delete(Ub_Client.HOST + "/v1/order", params=query, headers=headers)
        return res.json()


    def print_put(self, strword):
        self.total_print.append(strword)
        return 0

    def all_print(self):
        print("@@@@@@@@UPBIT@@@@@@@@")
        for i in range(len(self.total_print)):
            print(self.total_print[i])
        print("@@@@@@@@@@@@@@@@@@@@@")