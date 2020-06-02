# upbit 객체
import threading
import time

from account.keys import *
from algoset.larry_williams import *
from binance_bot.bn_Client import Bn_Client
from manager.manager import Manager
from upbit_bot.ub_Client import Ub_Client

ub_client = Ub_Client(ub_access_key, ub_secret_key)
bn_client = Bn_Client(bn_access_key, bn_secret_key)

aa = bn_client.get_day_candle("BTCUSDT", 300)
print(aa)

# # # 매니저 관리 프로그램 on
# ub_manager = Manager(ub_client)
#
# # # 업비트 변동성돌파전략
# ub_will = William(ub_manager, ["KRW-BTC", "KRW-ETH"])
# # 매니저 run
# managing = threading.Thread(target=Manager.main, args=())
# managing.start()
# time.sleep(3)
# # # 매니저 run
# # managing = threading.Thread(target=Manager.monitor, args=())
# # managing.start()

