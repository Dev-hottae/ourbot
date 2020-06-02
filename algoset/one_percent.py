import datetime
import threading
import time

import telegram
from apscheduler.schedulers.background import *

from account.keys import *
from manager.manager import Manager


class One_percent(threading.Thread):
    ALGO = "onepercent"

    def run(self):

        # 알고리즘에 금액할당
        self.money = Manager.MANAGER_ALGO_RUN[One_percent.ALGO][self.manager.client.EXCHANGE]

        # 스케쥴러 등록
        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(self.initializer, 'cron', hour=0, minute=0, second=0, id="initializer")

        while True:
            if (Manager.THREADING and self._run) is True:
                # 알고리즘에 금액할당
                money_alloc = self.money
                money = money_alloc / len(self.init_market)
                self.algo_onepercent(money)

            time.sleep(1)

    # One_percent(ub_manager, ["KRW-BTC", "KRW-ETH"])
    def __init__(self, manager, market):

        threading.Thread.__init__(self)
        # 텔레그램 세팅
        self.msg_bot = telegram.Bot(token=tg_token)

        self._run = True
        self.manager = manager
        self.fee = self.manager.client.TR_FEE

        # 매니저에 알고리즘 등록
        Manager.MANAGER_ALGO_RUN[One_percent.ALGO] = Manager.MANAGER_ALGO
        # ex ["KRW-BTC", "KRW-ETH"]
        self.init_market = market[:]
        self.run_market = []

        self.money = 0

        self.order_id = {}

        # 금일 타겟가
        self.target = {}
        self.sell_target = {}

        # 나머지 초기화
        self.initializer()

    def initializer(self):
        # 초기화 중 알고리즘 잠시 정지
        self._run = False

        # 전일 보유물량 취소 및 매도
        if len(self.order_id) > 0:
            order_list = list(self.order_id.values())
            for i in range(len(order_list)):
                req = self.manager.client.query_order(order_list[i])
                if (req[0]["status"] == "NEW") | (req[0]["status"] == "wait"):
                    self.manager.client.cancel_order(req[0])
                else:
                    if self.manager.client.EXCHANGE == "UB":
                        self.manager.client.new_order(req[0]['market'], 'ask', 'market', vol=req[0]['executed_volume'])

                    elif self.manager.client.EXCHANGE == "BN":
                        self.manager.client.new_order(req[0]["market"], "SELL", "MARKET", vol=req[0]['executed_volume'])

                    else:
                        pass

        self.order_id.clear()
        self.run_market = self.init_market[:]
        # 파라미터 초기화
        self.target = {}
        self.sell_target = {}

        for i in range(len(self.init_market)):
            self.target[self.init_market[i]] = self.target_price(self.init_market[i])
            self.sell_target[self.init_market[i]] = self.target[self.init_market[i]] * 1.01

        # 메세징
        ex = self.manager.client.EXCHANGE
        on_time = datetime.datetime.now().strftime('%Y-%m-%d')
        target = self.target

        msg = {
            "EX": ex,
            "Time": on_time,
            "Algo": One_percent.ALGO,
            "Balance": self.manager.MANAGER_ALGO_RUN[One_percent.ALGO][ex],
            "Target": target
        }

        self.send_msg(msg)

        # 재개
        self._run = True

    # 개별시장마다
    ## 일단 업비트만
    def algo_onepercent(self, money):
        for i in range(len(self.run_market)):
            market = self.run_market[i]
            try:
                current_price = self.manager.client.get_current_price(market)[0]['price']
            except Exception as e:
                print(e)
            else:
                if current_price >= self.target[market]:
                    order_id = self.manager.client.new_order(market, 'bid', 'price', money=money,
                                                             target=self.target[market])
                    time.sleep(1)

                    # 매수즉시 타겟가로 지정가매도주문
                    info = self.manager.client.query_order(order_id)[0]
                    sell_order = self.manager.client.new_order(market, 'ask', 'limit', vol=info['executed_volume'], target=self.sell_target[market])
                    # 매도주문정보입력!@!@!1 판다스 활용

                    self.order_id[market] = sell_order
                    self.run_market.remove(market)
                    break

    # 매수가 결정함수
    def target_price(self, market):
        day_before_data = self.manager.client.get_day_candle(market, 2)[1]
        close = float(day_before_data["trade_price"])
        high = float(day_before_data["high_price"])
        low = float(day_before_data["low_price"])

        target_Price = close + (high - low) * 0.5
        return target_Price

    # 텔레봇
    def send_msg(self, data):

        msg = "봇 알림!!\n"
        key_list = list(data.keys())
        for i in range(len(data)):
            msg += key_list[i]
            msg += " : "
            msg += str(data[str(key_list[i])])
            msg += "\n"

        # 메시지 전송
        self.msg_bot.send_message(chat_id=tg_my_id, text=msg)
