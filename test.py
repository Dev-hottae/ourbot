# ub_client = Ub_Client(ub_access_key, ub_secret_key)
# bn_client = Bn_Client(bn_access_key, bn_secret_key)
# print(time_checker())

#
# ub_will = William(ub_client, ["KRW-BTC", "KRW-ETH"])
# print(ub_will.param)
# print(ub_will.target)
#
#
# ub_william = threading.Thread(target=ub_will.algo_william, args=(3000,))
# ub_william.start()
#
# bn_will = William(bn_client, ["BTCUSDT"])
# print(bn_will.param)
# print(bn_will.target)
#
# bn_william = threading.Thread(target=bn_will.algo_william, args=(12,))
# bn_william.start()
#
# while True :
#     time.sleep(1)

# import requests
# from bs4 import BeautifulSoup
# webpage = requests.get("https://finance.yahoo.com/quote/KRW=X?p=KRW=X")
# soup = BeautifulSoup(webpage.content, "html.parser")
# soup = soup.select("#quote-header-info")
# print(soup)

# 매니저 관리 프로그램 on
# ub_manager = Manager(ub_client)
# bn_manager = Manager(bn_client)
# print(Manager.MANAGER)
# print(ub_manager==Manager.MANAGER[0])

copy = []
ori = []
ori.append("aa")
copy = ori[:]
copy.remove("aa")
print(copy)
print(ori)