import sched

import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests

from account import keys
from market_data.market_trade import get_target_price


def order(market, side, volume, price, ord_type):
    access_key = keys.access_key
    secret_key = keys.secret_key
    server_url = 'https://api.upbit.com'

    query = {
        'market': market,
        'side': side,
        'volume': volume,
        'price': price,
        'ord_type': ord_type,
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
    print(res.text)


get_url = "https://api.upbit.com/v1/candles/days"
querystring_BTC = {"market": "KRW-BTC", "count": "2", "convertingPriceUnit": "KRW"}
querystring_ETH = {"market": "KRW-ETH", "count": "2", "convertingPriceUnit": "KRW"}


def get_btc():
    # if (sched.get_job("order_btc") != None):
    #     sched.remove_job('order_btc')

    response_krw = requests.request("GET", get_url, params=querystring_BTC)
    prev_data_json = response_krw.json()[1]
    target_btc = get_target_price(prev_data_json)
    # sched.add_job(order_btc, 'interval', seconds=1, id="order_btc")


def get_eth():
    # if (sched.get_job("order_eht") != None):
    #     sched.remove_job('order_eth')
    response_krw = requests.request("GET", get_url, params=querystring_ETH)
    prev_data_json = response_krw.json()[1]
    target_eth = get_target_price(prev_data_json)
    # sched.add_job(order_eth, 'interval', seconds=1, id="order_eth")


def order_eth():
    print("??")
    pass


def order_btc():
    pass
