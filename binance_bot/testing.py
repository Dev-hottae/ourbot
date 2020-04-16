import datetime
import hashlib
import hmac
import time
from urllib.parse import urlencode

import requests

from account.keys import *
from binance_bot.bn_Client import Bn_Client

# 매수매도 주문함수
def order_bid(symbol, side, type, timeInForce, quantity, price):
    endpoint = "/api/v3/order"

    query = {
        "symbol": symbol,
        "side": side,
        "type": type,
        "timeInForce": timeInForce,
        "quantity": quantity,
        "price": price,
        "timestamp": int(time.time() * 1000)
    }

    query_string = urlencode(query)

    signature = hmac.new(bn_secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
    signature = str(signature.hexdigest())

    query["signature"] = signature

    header = {
        "X-MBX-APIKEY": bn_access_key
    }

    url = Bn_Client.HOST + endpoint

    res = requests.post(url, params=query, headers=header)
    return res.json()

data = order_bid("BTCUSDT", "BUY", "limit", "GTC", 0.1, 6800)

print(data)