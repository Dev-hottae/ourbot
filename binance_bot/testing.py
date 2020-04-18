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


def account_agg_balance():
    endpoint = "/api/v3/account"

    query = {
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

    res = requests.get(url, params=query, headers=header)
    account_all_info = res.json()["balances"]
    exist_bal = list(filter(lambda x: float(x["free"]) > 0, account_all_info))

    return exist_bal

print(account_agg_balance())