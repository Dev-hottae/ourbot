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

    # 주문 호출을 위한 함수
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
        res = res.json()

        # 주문 날리면 uuid 리턴
        return res["uuid"]


    # 현재 대기열에 있는 주문 uuid 들의 값들을 가져옴
    def uuids_by_state(self, situation, ordered_uuids):
        query = {
            'state': situation,
        }
        query_string = urlencode(query)

        uuids = ordered_uuids

        uuids_query_string = '&'.join(["uuids[]={}".format(uuid_) for uuid_ in uuids])
        query['uuids[]'] = uuids

        if len(uuids) == 0:
            return []

        query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.S_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.S_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(Ub_Client.HOST + "/v1/orders", params=query, headers=headers)

        return res.json()

    ## 자산 처분 실행
    # uuid 기반 보유 자산 처분 요청
    def sell_asset(self, id):
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
            'access_key': ub_access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, ub_secret_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.post(Ub_Client.HOST + "/v1/orders", params=query, headers=headers)

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


    # 오전 9시 현재 보유자산 처분 요청
    def request_sell(self):
        # 현재 주문 완료된 uuid 값들을 가져옴
        done_uuids = self.uuids_by_state('done', self.total_ordered_uid)
        print("매도해야할 uuid: " + str(done_uuids))
        if len(done_uuids) == 0:
            print("현재 매수완료된 주문의 건이 없습니다...")
            return
        print("총 %s 개의 자산을 보유하고 있습니다..." % len(done_uuids))

        for i in range(len(done_uuids)):
            self.sell_asset(done_uuids[i])
            print("처리된 uuid : " + str(done_uuids[i]))
        print("모든 보유자산의 매도가 정상 처리되었습니다....")

    # 오전9시 보유종목 매도 및 전체 등록 주문 취소
    def waits_order_cancel(self):
        # 현재 대기열에 있는 주문들 uuid 값들을 가져옴
        wait_uuids = self.uuids_by_state('wait', self.total_ordered_uid)
        print("대기중인 uuid : " + str(wait_uuids))
        if len(wait_uuids) == 0:
            print("현재 waiting 주문의 건이 없습니다...")
            return
        print("총 %s 건의 주문이 waiting 중입니다...." % len(wait_uuids))
        for i in range(len(wait_uuids)):
            self.order_cancel(wait_uuids[i])
            print("처리된 uuid : " + str(wait_uuids[i]))
        print("waiting 주문들의 취소가 정상 처리되었습니다...")



    def print_put(self, strword):
        self.total_print.append(strword)
        return 0

    def all_print(self):
        print("@@@@@@@@UPBIT@@@@@@@@")
        for i in range(len(self.total_print)):
            print(self.total_print[i])
        print("@@@@@@@@@@@@@@@@@@@@@")