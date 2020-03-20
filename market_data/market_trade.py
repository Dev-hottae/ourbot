import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
from account import keys
import requests

from account.login import account_info

prev_data = [
    {
        "market": "KRW-BTC",
        "candle_date_time_utc": "2018-04-18T00:00:00",
        "candle_date_time_kst": "2018-04-18T09:00:00",
        "opening_price": 8450000,
        "high_price": 8679000,
        "low_price": 8445000,
        "trade_price": 8626000,
        "timestamp": 1524046650532,
        "candle_acc_trade_price": 107184005903.68721,
        "candle_acc_trade_volume": 12505.93101659,
        "prev_closing_price": 8450000,
        "change_price": 176000,
        "change_rate": 0.0208284024
    }
]

access_key = keys.access_key
secret_key = keys.secret_key
server_url = 'https://api.upbit.com'


def get_target_price(coin_price):
    target_price = 0
    parameter = 0  ## 이후 메인함수로 빼내야함
    open = int(coin_price["opening_price"])
    close = int(coin_price["trade_price"])
    high = int(coin_price["high_price"])
    low = int(coin_price["low_price"])

    target_price = open + (high - low) * parameter

    return target_price


def buying_price_cal(prev_data, parameter):
    open = prev_data[0]['opening_price']
    high = prev_data[0]['high_price']
    low = prev_data[0]['low_price']
    parameter = parameter

    buying_price = open + (high - low) * parameter

    return buying_price


def current_data():
    return 0


# 윌리엄 로직에 따른 매수 실행함수
def trade_bid(json_data, parameter):
    buying_price = json_data.json()[0]
    market = json_data.json()[0]

    current_balance = account_info().json()[0].get('balance')
    volume = (current_balance / 2) / buying_price  # 전체 잔고 중 절반

    query = {
        'market': market,
        'side': 'bid',
        'volume': volume,
        'price': buying_price,
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


# 매 9시마다 포지션 청산(시장가보다는 opening price 지정가로)
def trade_ask():
    pass
