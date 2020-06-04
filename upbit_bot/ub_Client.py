import datetime
import hashlib
import time
import uuid
from urllib.parse import urlencode

import jwt
import numpy
import requests
from pytz import timezone

from upbit_bot.config.realtype import RealType


class Ub_Client():
    EXCHANGE = "UB"
    HOST = 'https://api.upbit.com'
    DEFAULT_UNIT = "KRW"

    TR_FEE = 0.002

    def __init__(self, api_key, sec_key):
        self.A_key = api_key
        self.S_key = sec_key

        self.realtype = RealType()

        # william 알고리즘 위한 데이터 세팅
        self.W1_data_amount_for_param = 200  # max limit 이 200개

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

    # 코드리스트 요청
    def get_code_list(self, market_code):
        pass

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

        response = requests.request("GET", url, params=querystring).json()

        data = []
        data_dict = {
            'market': market,
            "price": float(response[0]['trade_price'])
        }
        data.append(data_dict)

        return data

    # 시장가/지정가 매수매도
    def new_order(self, market, side, ord_type, vol=None, money=None, target=None):

        if (target and money) is not None:
            target = self.price_cal(market, target)
            vol = round(money/target, 8)

        elif target is not None:
            target = self.price_cal(market, target)

        if ord_type == "limit":
            query = {
                'market': market,
                'side': side,
                'volume': vol,
                'price': target,
                'ord_type': "limit",
            }
        elif ord_type == "price":
            query = {
                'market': market,
                'side': side,
                'price': money,
                'ord_type': "price",
            }
        elif ord_type == "market":
            query = {
                'market': market,
                'side': side,
                'volume': vol,
                'ord_type': "market",
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

        res = requests.post(Ub_Client.HOST + "/v1/orders", params=query, headers=headers).json()
        print(res)
        if res['ord_type'] == 'limit':
            ord_price = res['price']
            ord_volume = res['volume']

        else:
            ord_price = None
            ord_volume = None

        data = []
        data_dict = {
            "market": res['market'],
            "side": res['side'],
            "ord_type": res['ord_type'],
            "ord_price": ord_price,
            "ord_volume": ord_volume,
            "uuid": res['uuid']
        }
        data.append(data_dict)

        return data

    # 개별 주문 조회
    def query_order(self, req):
        query = {
            'uuid': req[0]['uuid'],
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

        res = requests.get(Ub_Client.HOST + "/v1/order", params=query, headers=headers).json()

        if len(res['trades']) > 0:
            ord_price = res['trades'][0]['price']
            ord_volume = res['trades'][0]['volume']

        else:
            ord_price = res['price']
            ord_volume = res['volume']

        data = []
        data_dict = {
            "market": res['market'],
            "created_at": res['created_at'],
            "side": res['side'],
            "ord_type": res['ord_type'],
            "status": res["state"],
            "uuid": res['uuid'],
            "ord_price": ord_price,
            "ord_volume": ord_volume,
            "executed_volume": res["executed_volume"]
        }
        data.append(data_dict)

        return data

    ## uuid 기반 기주문 취소 요청
    def cancel_order(self, req):
        query = {
            'uuid': req["uuid"],
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

        res = requests.delete(Ub_Client.HOST + "/v1/order", params=query, headers=headers).json()

        return res

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

    def price_cal(self, market, ord_price):
        if ord_price < 10:
            min_unit = 0.01
        elif ord_price < 100:
            min_unit = 0.1
        elif ord_price < 1000:
            min_unit = 1
        elif ord_price < 10000:
            min_unit = 5
        elif ord_price < 100000:
            min_unit = 10
        elif ord_price < 500000:
            min_unit = 50
        elif ord_price < 1000000:
            min_unit = 100
        elif ord_price < 2000000:
            min_unit = 500
        else:
            min_unit = 1000

        # 타겟 가격 보다 올림가격
        poss_price = numpy.ceil(ord_price / min_unit) * min_unit
        return round(poss_price, 2)

