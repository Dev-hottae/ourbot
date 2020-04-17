import datetime
import hashlib
import hmac
import time
import numpy
from urllib.parse import *

import requests

from account.keys import *
from binance_bot.bn_Client import Bn_Client


total_ordered_uid = []

# 매수매도 주문함수 _stoplimit
def new_order_stoplimit(symbol, side, type, timeInForce, quantity, price, stopPrice):
    endpoint = "/api/v3/order/test"

    query = {
        "symbol": symbol,
        "side": side,
        "type": type,
        "timeInForce": timeInForce,
        "quantity": quantity,
        "price": price,
        "stopPrice": stopPrice,
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

    print(res.json())

    if side == "BUY":
        # 주문 id 저장
        ordered_info = []
        ordered_symbol = res.json()[0]["symbol"]
        orderId = res.json()["orderId"]

        ordered_info.append(ordered_symbol)
        ordered_info.append(orderId)
        total_ordered_uid.append(ordered_info)

    return res.json()

new_order_stoplimit("BTCUSDT", "BUY", "STOP_LOSS_LIMIT", "GTC", 0.01, 6000, 6000)