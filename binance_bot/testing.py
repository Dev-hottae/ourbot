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

bn_client = Bn_Client(bn_access_key, bn_secret_key)

# 과거 데이터 요청
prev_btc_data = bn_client.prev_data_request("BTCUSDT", bn_client.W1_data_amount_for_param)
prev_eth_data = bn_client.prev_data_request("ETHUSDT", bn_client.W1_data_amount_for_param)
prev_bnb_data = bn_client.prev_data_request("BNBUSDT", bn_client.W1_data_amount_for_param)

# 파라미터 계산
parameter_btc = william_param(prev_btc_data, Bn_Client.BN_FEE)
print("btc 최적파라미터 : " + str(parameter_btc))
parameter_eth = william_param(prev_eth_data, Bn_Client.BN_FEE)
print("eth 최적파라미터 : " + str(parameter_eth))
parameter_bnb = william_param(prev_bnb_data, Bn_Client.BN_FEE)
print("bnb 최적파라미터 : " + str(parameter_bnb))

print("----- 파라미터 수정 완료!! -----")