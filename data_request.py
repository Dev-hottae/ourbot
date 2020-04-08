import hashlib
import json
from urllib.parse import urlencode

import uuid
import jwt
import requests

from account.keys import *

get_url = "https://api.upbit.com/v1/candles/days"


# 현재 계정 데이터 요청
def account_info():
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    res = requests.get(server_url + "/v1/accounts", headers=headers)
    return res.json()


# 현재 대기열에 있는 주문 uuid 들의 값들을 가져옴
def uuids_by_state(situation, ordered_uuids):
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
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/orders", params=query, headers=headers)

    print("?", res.json())
    return res.json()


# day candle 요청

#### 일단위 캔들요청 수정본
def get_day_candle(market, count):
    querystring = {"market": str(market), "count": str(count), "convertingPriceUnit": "KRW"}
    response_krw = requests.request("GET", get_url, params=querystring)
    prev_data_json = response_krw.json()
    return prev_data_json


# 현재가 데이터를 가져오기위한 함수
def get_current_price(market):
    url = "https://api.upbit.com/v1/ticker"
    querystring = {"markets": market}
    response = json.loads(requests.request("GET", url, params=querystring).text)
    current_price = response[0]["trade_price"]
    print("현재 %s 가격 : " % market, current_price)
    return current_price
