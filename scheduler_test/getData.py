# 스케줄 종류에는 여러가지가 있는데 대표적으로 BlockingScheduler, BackgroundScheduler 입니다
# BlockingScheduler 는 단일수행에, BackgroundScheduler은 다수 수행에 사용됩니다.
# 여기서는 BackgroundScheduler 를 사용하겠습니다.
import json

from PyQt5.QtWidgets import QApplication
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

import time

import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests

from account import keys


def order(market,side,volume,price,ord_type):
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
# get data
querystring_BTC = {"market":"KRW-BTC","count":"2","convertingPriceUnit":"KRW"}
querystring_ETH = {"market":"KRW-ETH","count":"2","convertingPriceUnit":"KRW"}

btc_data =""
eth_data =""


def get_btc():
    response_krw = requests.request("GET", get_url, params=querystring_BTC)
    # print("KRW: "
    #       , str(time.localtime().tm_hour) + ":"
    #       + str(time.localtime().tm_min) + ":"
    #       + str(time.localtime().tm_sec))
    prev_data_json = response_krw.json()[1]
    # jsonString = json.dumps(response_krw.json()[1], indent=4)
    global btc_data
    # btc_data=jsonString
    get_target_price(prev_data_json)
    # print(response_krw)



def get_eth():
    response_krw = requests.request("GET", get_url, params=querystring_ETH)
    # print("ETH: "
    #       , str(time.localtime().tm_hour) + ":"
    #       + str(time.localtime().tm_min) + ":"
    #       + str(time.localtime().tm_sec))
    prev_data_json = response_krw.json()[1]
    # jsonString = json.dumps(response_krw.json()[1], indent=4)
    global eth_data
    # eth_data = jsonString
    get_target_price(prev_data_json)
    # print(eth_data)

def get_target_price(coin_price):
    target_price = 0

    open = int(coin_price["opening_price"])
    print(open)
    # close = coin_price["opening_price"]
    # high = coin_price["opening_price"]
    # low = coin_price["opening_price"]


    return target_price
# BackgroundScheduler 를 사용하면 stat를 먼저 하고 add_job 을 이용해 수행할 것을 등록해줍니다.

# order('KRW-GTO','ask','90','17','limit')