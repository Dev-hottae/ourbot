import sys

from PyQt5.QtWidgets import QApplication

from account.keys import *
from binance_bot.bn_Client import Bn_Client
from kiwoom_bot.kw_Client import Kw_Client
from upbit_bot.ub_Client import Ub_Client


# app = QApplication(sys.argv)
ub_client = Ub_Client(ub_access_key, ub_secret_key)
bn_client = Bn_Client(bn_access_key, bn_secret_key)
kw_client = Kw_Client()
#
print("accountinfo")
aa = ub_client.account_info()
# bb = bn_client.account_info()
cc = kw_client.account_info()
print(aa)
# print(bb)
print(cc)
print("--------------------------")
print("--------------------------")
print("getdaycandle")
aa = ub_client.get_day_candle("KRW-ETH",2)
# bb = bn_client.get_day_candle("ETHUSDT",2)
cc = kw_client.get_day_candle('069500', 2)
print(aa)
# print(bb)
print(cc)
print("--------------------------")
print("--------------------------")
print("getcurrentprice")
aa = ub_client.get_current_price("KRW-ETH")
# bb = bn_client.get_current_price("ETHUSDT")
cc = kw_client.get_current_price('069500')
print(aa)
# print(bb)
print(cc)
print("--------------------------")
print("--------------------------")
print("neworder")
# # 인풋값을 맞출수있도록
aa = ub_client.new_order("KRW-ETH", 'bid', 'price', money=1400.1234412)
# bb = bn_client.new_order('ETHUSDT', 'bid', 'price', money=12.30130810)
# print(aa)
# print(bb)
# cc = kw_client.new_order('069500')
# print(aa)
# print("[{'market': 'ETHUSDT', 'side': 'BUY', 'ord_type': 'STOP_LOSS_LIMIT', 'ord_price': '253.99000000', 'ord_volume': '0.04593000', 'uuid': 1176499993}]")
# print("--------------------------")
# print("--------------------------")
print('queryorder')
# aa = ub_client.query_order(aa)
# bb = bn_client.query_order(bb)
# print(aa)
# print(bb)
# print("--------------------------")
# print("--------------------------")


