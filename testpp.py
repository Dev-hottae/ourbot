# upbit 객체
import threading
import time

from account.keys import *
from algoset.larry_williams import *
from binance_bot.bn_Client import Bn_Client
from manager.manager import Manager
from upbit_bot.ub_Client import Ub_Client
import pandas as pd

ub_client = Ub_Client(ub_access_key, ub_secret_key)
pp = ub_client.new_order("KRW-ETH", 'bid', 'price', money=1500)

ppp = ub_client.query_order(pp)[0]
aa = ub_client.new_order("KRW-ETH", 'ask', 'market', ppp['executed_volume'])
print(aa)

# pp = ub_client.account_info()
# print(pp)
# data = {'currency': 'KRW', 'balance': '58014.08948678', 'locked': '0.0', 'avg_buy_price': '0', 'avg_buy_price_modified': True, 'unit_currency': 'KRW'}


# dataframe = pd.DataFrame([{}])
# dataframe.to_csv('datacsv.csv', mode='a', header=True, index=False)
# print(dataframe)
# data = pd.read_csv('./datacsv.csv').to_dict('records')
# print(data)
# data = data
# print(data)

# bn_client = Bn_Client(bn_access_key, bn_secret_key)
#
# aa = bn_client.get_day_candle("BTCUSDT", 300)
# print(aa)

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





