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

ub_client = Ub_Client(ub_access_key, ub_secret_key)
app = QApplication(sys.argv)
kw_client = Kw_Client()
#
ub = ub_client.get_day_candle("KRW-BTC",2)
print(ub)
kw = kw_client.get_day_candle("000087", 2)
print(kw)
print(type(kw[0]['candle_date_time_kst']))
datetime
# app.exec_()
