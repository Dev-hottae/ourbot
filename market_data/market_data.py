import os
from multiprocessing import Process
import jwt
import uuid
import hashlib
import websocket, json, time
import requests
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

try:
    import thread
except ImportError:
    import _thread as thread

# 변수선언
response = None
market_data = None


class Market_datas(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, market, url):
        super().__init__()
        self.market_data_array = market  # 데이터를 받을 시장
        self.url = url

    def run(self):

        while True:

            data = {}
            for market in self.market_data_array:
                data[market] = Market_data(market, self.url)

            self.finished.emit(data)
            time.sleep(1)


    def update_marketdata(self, data):

        btc_price = int(data[self.market_data_array[0]][0]['trade_price'])
        # if btc_price >= buying_price_cal(prev_data, parameter):
        #     order(market,side,volume,price,ord_type)
        eth_price = int(data[self.market_data_array[1]][0]['trade_price'])

        print("BTC 현재가 : %s KRW" % btc_price)
        print("ETH 현재가 : %s KRW" % eth_price)

        QApplication.processEvents()


# Market Data Management
def Market_data(market, url):
    # 단순 ticker 데이터 1회 수신
    url = url
    querystring = {"markets": market}
    response = json.loads(requests.request("GET", url, params=querystring).text)

    return response