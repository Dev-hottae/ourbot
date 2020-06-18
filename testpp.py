import threading
import time

from account.keys import *
from algoset.one_percent_10min import One_percent_10min
from manager.manager import Manager
from upbit_bot.ub_Client import Ub_Client

print('클라이언트 셋')
ub_client = Ub_Client(ub_access_key, ub_secret_key)
print('manager set')
ub_manager = Manager(ub_client)

print('algo set')
ub_one_10min = One_percent_10min(ub_manager)

managing = threading.Thread(target=Manager.main, args=())
managing.start()

ub_one_10min.start()

while True:
    time.sleep(1000)