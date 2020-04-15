import datetime
import hashlib
import hmac
import time
from urllib.parse import urlencode
from algoset.larry_williams import *
import requests

from binance_bot.bn_main import org_data


class Client(org_data):
    HOST = "https://api.binance.com"
    BN_FEE = 0.0015 # account_info 호출하면 나옴 이후에 변경할 것

    def __init__(self, API_key, Secret_key):
        super().__init__()
        self.API_key = API_key
        self.S_key = Secret_key

    # My account 데이터 호출
    def account_info(self):
        endpoint = "/api/v3/account"

        query = {
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.API_key
        }

        url = Client.HOST + endpoint

        res = requests.get(url, params=query, headers=header)
        return res.json()

    # 현재 달러 기준으로 잔고 확인
    def account_agg_balance(self):
        pass

    # 과거 데이터 호출
    def prev_data_request(self, market, limit, interval="1d"):
        endpoint = "/api/v3/klines"

        query = {
            "symbol": market,
            "interval": interval,
            "limit": limit
        }

        url = Client.HOST + endpoint

        res = requests.get(url, params=query)
        data = res.json()
        data_list = []

        for i in range(len(data)-1, -1, -1):
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
    
    # 현재가 호출
    def current_price(self, symbol):
        endpoint = "/api/v3/ticker/price"
        query = {
            "symbol": symbol
        }

        url = Client.HOST + endpoint

        res = requests.get(url, params=query)
        return res.json()



    ### 이후 모듈로 분리
    # 타겟 가격 설정
    def set_target_price(self, market):
        prev_price_data = self.prev_data_request(self, market, 365)

        yester_close = prev_price_data[1]["close"]
        yester_high = prev_price_data[1]["high"]
        yester_low = prev_price_data[1]["low"]

        param = william_param(prev_price_data, Client.BN_FEE)

        target_price = yester_close + (yester_high - yester_low) * param

        # target_price float 형식으로 리턴
        return target_price







'''
def servertime_checking():
    int(time.time() * 1000) - client.get_server_time()['serverTime']
    for i in range(1, 10):
        local_time1 = int(time.time() * 1000)
        server_time = client.get_server_time()
        diff1 = server_time['serverTime'] - local_time1
        local_time2 = int(time.time() * 1000)
        diff2 = local_time2 - server_time['serverTime']
        print("local1: %s server:%s local2: %s diff1:%s diff2:%s" % (
            local_time1, server_time['serverTime'], local_time2, diff1, diff2))
        time.sleep(2)
'''