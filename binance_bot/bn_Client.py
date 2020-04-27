import datetime
import hashlib
import hmac
import time
from urllib.parse import *

from pytz import timezone

from algoset.larry_williams import *
import requests


class Bn_Client():
    HOST = "https://api.binance.com"

    BN_FEE = 0.0015  # account_info 호출하면 나옴 이후에 변경할 것

    COIN_MIN_TRADE_AMOUNT = 0.000001

    BTC_MIN_UNIT = 0.01
    ETH_MIN_UNIT = 0.01
    BNB_MIN_UNIT = 0.0001

    def __init__(self, api_key, sec_key):
        self.A_key = api_key
        self.S_key = sec_key

        # 주문 정보
        self.yesterday_uid = []
        self.total_ordered_uid = []

        # 전체 콘솔 프린트
        self.total_print = []

        # 내 잔고
        self.my_account = self.account_info()
        self.my_rest_balance = None
        self.my_total_balance = None

        # william 알고리즘 위한 금액 세팅
        self.W1_btc_money = 0
        self.W1_eth_money = 0
        self.W1_bnb_money = 0
        self.W1_btc_rate = 0.32
        self.W1_eth_rate = 0.32
        self.W1_bnb_rate = 0.32

        self.W1_data_amount_for_param = 365

    # My account 데이터 호출
    def account_info(self, recvWindow=60000):
        endpoint = "/api/v3/account"

        query = {
            "recvWindow": recvWindow,
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint

        res = requests.get(url, params=query, headers=header)

        # 리턴할때 버퍼가 작은 듯
        res = res.json()["balances"]
        return res

    # 현재 보유 잔고 확인
    def account_having_balance(self):
        account_all_info = self.account_info()
        exist_bal = list(filter(lambda x: float(x["free"]) > 0, account_all_info))

        return exist_bal

    # 현재 달러기준 전체 잔고 확인
    def account_agg_bal(self):
        pass


    # 과거 데이터 호출
    def prev_data_request(self, market, limit, interval="1d"):
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

    # 현재가 호출
    def current_price(self, symbol):
        endpoint = "/api/v3/ticker/price"
        query = {
            "symbol": symbol
        }

        url = Bn_Client.HOST + endpoint

        res = requests.get(url, params=query)
        return res.json()

    # 매수매도 주문함수 _limit
    def new_order_limit(self, symbol, side, type, timeInForce, quantity, price, recvWindow=60000):
        endpoint = "/api/v3/order"

        query = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "timeInForce": timeInForce,
            "quantity": quantity,
            "price": price,
            "recvWindow": recvWindow,
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint

        res = requests.post(url, params=query, headers=header)

        if side == "BUY":
            # 주문 id 저장
            ordered_info = []
            print(res.json())
            ordered_symbol = res.json()["symbol"]
            orderId = res.json()["orderId"]

            ordered_info.append(ordered_symbol)
            ordered_info.append(orderId)
            self.total_ordered_uid.append(ordered_info)

        return res.json()

    # 매수매도 주문함수 _market
    def new_order_market(self, symbol, side, type, quantity, recvWindow=60000):
        endpoint = "/api/v3/order"

        query = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "quantity": quantity,
            "recvWindow": recvWindow,
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint

        res = requests.post(url, params=query, headers=header)

        if side == "BUY":
            # 주문 id 저장
            ordered_info = []
            ordered_symbol = res.json()["symbol"]
            orderId = res.json()["orderId"]

            ordered_info.append(ordered_symbol)
            ordered_info.append(orderId)
            self.total_ordered_uid.append(ordered_info)

        return res.json()

    # 매수매도 주문함수 _stoplimit
    def new_order_stoplimit(self, symbol, side, type, timeInForce, quantity, price, stopPrice, recvWindow=60000):
        endpoint = "/api/v3/order"

        query = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "timeInForce": timeInForce,
            "quantity": quantity,
            "price": price,
            "stopPrice": stopPrice,
            "recvWindow": recvWindow,
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint

        res = requests.post(url, params=query, headers=header)

        if side == "BUY":
            # 주문 id 저장
            ordered_info = []
            ordered_symbol = res.json()["symbol"]
            orderId = res.json()["orderId"]

            ordered_info.append(ordered_symbol)
            ordered_info.append(orderId)
            self.total_ordered_uid.append(ordered_info)

        return res.json()

    # 주문 취소
    def cancel_order(self, symbol, orderid, recvWindow=60000):
        endpoint = "/api/v3/order"

        query = {
            "symbol": symbol,
            "orderId": orderid,
            "recvWindow": recvWindow,
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint
        res = requests.delete(url, params=query, headers=header)

        return res.json()

    # id 기반 주문 쿼리
    def query_order(self, symbol, orderid, recvWindow=60000):
        endpoint = "/api/v3/order"

        query = {
            "symbol": symbol,
            "orderId": orderid,
            "recvWindow": recvWindow,
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint
        res = requests.get(url, params=query, headers=header)

        return res.json()


    def print_put(self, strword):
        self.total_print.append(strword)
        return 0

    def all_print(self):
        print("@@@@@@@@BINANCE@@@@@@")
        for i in range(len(self.total_print)):
            print(self.total_print[i])
        print("@@@@@@@@@@@@@@@@@@@@@")