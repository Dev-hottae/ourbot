import hashlib
import uuid
from urllib.parse import urlencode

import jwt
import requests

from account.keys import *


## 자산 처분 실행
# uuid 기반 보유 자산 처분 요청
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


## uuid 기반 기주문 취소 요청
def order_cancel(id):
    query = {
        'uuid': id["uuid"],
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

    res = requests.delete(server_url + "/v1/order", params=query, headers=headers)


## 매수주문

# 목표 매수가 돌파 시 주문 호출을 위한 함수
def order_bid(market, target_price, money_for_bid, unit):
    print(market, '주문실행...')
    price = int((target_price // unit) * unit)
    volume = "{0:.8f}".format(money_for_bid / price)
    query = {
        'market': market,
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

    # 주문 날리면 uuid 리턴
    return res["uuid"]
