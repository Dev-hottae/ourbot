# upbit 객체
import threading

from account.keys import *
from binance_bot.bn_Client import Bn_Client
from manager.manager import Manager
from upbit_bot.ub_Client import Ub_Client

ub_client = Ub_Client(ub_access_key, ub_secret_key)

bn_client = Bn_Client(bn_access_key, bn_secret_key)
# # 매니저 관리 프로그램 on
ub_manager = Manager(ub_client)
bn_manager = Manager(bn_client)

bb = Manager.MANAGER_TOTAL_MONEY
cc = Manager.MANAGER_ALGO
print("cc")
print(cc)
print(bb)
pp = ub_manager.m_set_money()
print(pp)

# # 매니저 run
# managing = threading.Thread(target=Manager.monitor, args=())
# managing.start()

