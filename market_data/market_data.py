import os
from multiprocessing import Process
import jwt
import uuid
import hashlib
import websocket, json, time
import requests
from PyQt5.QtCore import *

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
        self.market_data_array = market     # 데이터를 받을 시장
        self.url = url
    def run(self):
        while True:
            data = {}

            for market in self.market_data_array:
                data[market] = Market_data(market, self.url)

            self.finished.emit(data)
            time.sleep(0.1)

# Market Data Management
def Market_data(market, url):

    # 단순 ticker 데이터 1회 수신
    url = url
    querystring = {"markets": market}
    response = json.loads(requests.request("GET", url, params=querystring).text)

    return response


    # 웹 소켓으로 데이터 지속수신
    # websocket.enableTrace(True)
    # ws = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
    #                             on_open=on_open,
    #                             on_message=on_message,
    #                             on_error=on_error,
    #                             on_close=on_close)

    # ws.on_open = on_open
    # ws.run_forever()


# def on_message(ws, message):
#     json_data = json.loads(message)
#     print(json_data)
#
# def on_error(ws, error):
#     print(error)
#
# def on_close(ws):
#     print("### closed ###")
#
#
# def on_open(ws):
#
#     def run(*args):
#         ws.send(json.dumps(
#         [{"ticket": "test"}, {"type": "ticker", "codes": [market_data]}]))
#     run()
#     # thread.start_new_thread(run, ())