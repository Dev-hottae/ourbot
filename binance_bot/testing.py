import datetime
import hashlib
import hmac
import time
import uuid
from decimal import Decimal

import jwt
import numpy
from urllib.parse import *

import requests
from pytz import timezone

from account.keys import *
import ntplib
# from time import ctime
import socket
import struct
import sys
import time
import datetime
import win32api
import subprocess

from algoset.larry_williams import william_param
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

    last_data_time = datetime.datetime.fromtimestamp(data[limit-1][0] / 1000, timezone('UTC')).isoformat()
    on_time = datetime.datetime.now(timezone('UTC')).strftime('%Y-%m-%d')

    timer = 0
    while (on_time not in last_data_time) | (timer == 10):
        res = requests.get(url, params=query)
        data = res.json()
        timer += 1
        time.sleep(1)

    data_list = []

    for i in range(len(data) - 1, -1, -1):
        _time = datetime.datetime.fromtimestamp(data[i][0] / 1000).isoformat()
        open = float(data[i][1])
        high = float(data[i][2])
        low = float(data[i][3])
        close = float(data[i][4])

        one_data = {
            "candle_date_time_kst": _time,
            "opening_price": open,
            "high_price": high,
            "low_price": low,
            "trade_price": close
        }
        data_list.append(one_data)

    return data_list

data = prev_data_request("BNBUSDT", 20, interval="1d")
for i in range(len(data)):
    print(data[i]["candle_date_time_kst"],"\t", data[i]["opening_price"],"\t", data[i]["high_price"],"\t", data[i]["low_price"],"\t", data[i]["trade_price"])