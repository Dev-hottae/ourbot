import datetime
import hashlib
import hmac
import time
import numpy
from urllib.parse import *

import requests
from pytz import timezone

from account.keys import *
from binance_bot.bn_Client import Bn_Client
from upbit_bot.ub_Client import Ub_Client

# 과거 데이터 호출
def prev_data_request(market, limit, interval="1d"):
    endpoint = "/api/v3/klines"

    query = {
        "symbol": market,
        "interval": interval,
        "limit": limit
    }

    url = Bn_Client.HOST + endpoint

    res = requests.get(url, params=query)
    data = res.json()

    last_data_time = datetime.datetime.fromtimestamp(data[limit - 1][0] / 1000, timezone('UTC')).isoformat()
    on_time = datetime.datetime.now(timezone('UTC')).strftime('%Y-%m-%d')

    print(last_data_time)
    print(on_time)

    timer = 0
    while (on_time not in last_data_time) | (timer == 500):
        res = requests.get(url, params=query)
        data = res.json()
        timer += 1

    data_list = []

    for i in range(len(data) - 1, -1, -1):
        time = datetime.datetime.fromtimestamp(data[i][0] / 1000).isoformat()
        open = float(data[i][1])
        high = float(data[i][2])
        low = float(data[i][3])
        close = float(data[i][4])

        one_data = {
            "candle_date_time_kst": time,
            "opening_price": open,
            "high_price": high,
            "low_price": low,
            "trade_price": close
        }
        data_list.append(one_data)

    return data_list

dataa = prev_data_request("BTCUSDT", 3, interval="1d")
print(dataa)