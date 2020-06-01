import time

import telegram
from apscheduler.schedulers.background import *

from account.keys import *
from manager.manager import Manager


class One_percent():
    ALGO = "onepercent"

    # One_percent(ub_manager, ["KRW-BTC", "KRW-ETH"])
    def __init__(self, manager, market):

        # 텔레그램 세팅
        self.msg_bot = telegram.Bot(token=tg_token)

        self._run = True
        self.manager = manager
        self.fee = self.manager.client.TR_FEE

        # 매니저에 알고리즘 등록
        Manager.MANAGER_ALGO_RUN[self.manager.exchange].append(One_percent.ALGO)

        # ex ["KRW-BTC", "KRW-ETH"]
        self.init_market = market[:]
        self.run_market = market[:]

        # 금일 타겟가
        self.target = {}

        # 주문 성공내역
        self.order_id = []

    def initializer(self):
        # 초기화 중 알고리즘 잠시 정지
        self._run = False

        pass

    def main(self):
        # 스케쥴러 등록
        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(self.initializer, 'cron', hour=0, minute=0, second=0, id="initializer")

        while True:
            if self._run is True:
                money_alloc = self.money[self.manager.exchange] * 0.95
                money = money_alloc / len(self.init_market)
                self.algo_onepercent(money)

            time.sleep(0.5)

    # 개별시장마다
    def algo_onepercent(self, money):
        for i in range(len(self.run_market)):
            market = self.run_market[i]
            try:
                current_price = self.manager.client.get_current_price(market)[0]['price']
            except Exception as e:
                print(e)
            else:
                if current_price >= self.target[market]:
                    order_id = self.manager.client.new_order(market, 'bid', 'price', money)
                    self.order_id.append(order_id)
                    self.run_market.remove(market)
                    break

