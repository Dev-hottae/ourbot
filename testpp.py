# upbit 객체
import sys
import threading
import time

from PyQt5.QtWidgets import QApplication

from account.keys import *
from algoset.larry_williams import *
from binance_bot.bn_Client import Bn_Client
from kiwoom_bot.kw_Client import Kw_Client
from manager.manager import Manager
from upbit_bot.ub_Client import Ub_Client
import pandas as pd

# ub_client = Ub_Client(ub_access_key, ub_secret_key)
app = QApplication(sys.argv)
kw_client = Kw_Client()
#
# ub = ub_client.get_current_price("KRW-ETH")
# print(ub)
kw = kw_client.new_order('000087', 'bid', '시장가', vol=1)
print(kw)
# aa = kw_client.price_cal('000087')
# print(aa)
#
# cc = kw_client.price_cal('005380')
# dd = kw_client.price_cal('196170')
# print(bb)
# print(cc)
# print(dd)
# app.exec_()
