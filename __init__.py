import sys

from account.login import *
from scheduler_test.getData import *
from market_data.market_data import *
from apscheduler.schedulers.background import BackgroundScheduler

## 기본 변수설정
# account 관련변수
account_data = None

# 시장가격 데이터 호출 관련 변수
market = ["KRW-BTC", "KRW-ETH"]
current_price_url = "https://api.upbit.com/v1/ticker"
prev_price_url = "https://api.upbit.com/v1/candles/days"
info_url = "https://api.upbit.com/v1/candles/days"

global prev_btc_data
global prev_eth_data

## 실제 실행
# My account 정보 호출 // 잔고 변화 이벤트 있을 시 수시 호출 가능하게 변경할 것

account_data = account_info()
my_balance = account_data.json()[0].get('balance')
my_balance = str(round(float(my_balance), 3))
main_currency = account_data.json()[0].get('currency')
print("현재 My account Balance : " + my_balance + main_currency)

# 시장 현재가 데이터 호출(쓰레드 분리)
app = QApplication(sys.argv)
price_helper = Market_datas(market, current_price_url)
price_helper.finished.connect(price_helper.update_marketdata)
price_helper.start()

# 스케쥴러 등록
sched = BackgroundScheduler()
sched.start()
# 스케쥴 테스트용
sched.add_job(get_btc, 'interval', seconds=5, id="get_btc")
sched.add_job(get_eth, 'interval', seconds=5, id="get_etc")

# 스케쥴 매9시 실행
# sched.add_job(get_btc, 'cron', hour=9, id="get_btc")
# sched.add_job(get_eth, 'cron', hour=9, id="get_etc")

app.exec_()
