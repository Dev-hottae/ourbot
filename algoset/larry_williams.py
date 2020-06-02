import datetime
import operator
import threading
import time

import numpy
import telegram
from apscheduler.schedulers.background import BackgroundScheduler

from account.keys import *
from manager.manager import Manager


class William(threading.Thread):
    ALGO = "william"

    def run(self):

        # 알고리즘에 금액할당
        self.money = Manager.MANAGER_ALGO_RUN[William.ALGO][self.manager.client.EXCHANGE]

        # 스케쥴러 등록
        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(self.initializer, 'cron', hour=0, minute=0, second=0, id="initializer")

        while True:
            if (Manager.THREADING and self._run) is True:
                # 알고리즘에 금액할당
                money_alloc = self.money
                money = money_alloc / len(self.init_market)
                self.algo_william(money)

            time.sleep(1)

    # William(ub_manager, ["KRW-BTC", "KRW-ETH"])
    def __init__(self, manager, market):

        threading.Thread.__init__(self)
        self.msg_bot = telegram.Bot(token=tg_token)

        self._run = True
        self.manager = manager
        self.fee = self.manager.client.TR_FEE

        # 매니저에 알고리즘 등록
        Manager.MANAGER_ALGO_RUN[William.ALGO] = Manager.MANAGER_ALGO

        # ["KRW-BTC", "KRW-ETH"]
        self.init_market = market[:]
        self.run_market = []
        self.data_amount = self.manager.client.W1_data_amount_for_param
        self.money = 0

        self.order_id = []

        # 파라미터 초기화
        self.param = {}
        self.target = {}

        # 나머지 초기화
        self.initializer()

    # 매 정시 파라미터 타겟 가격 초기화
    def initializer(self):
        self._run = False

        # 전일 보유물량 매도
        if len(self.order_id) > 0:
            for i in range(len(self.order_id)):
                req = self.manager.client.query_order(self.order_id[i])
                if (req[0]["status"] == "NEW") | (req[0]["status"] == "wait"):
                    self.manager.client.cancel_order(req)
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
        self.param = {}
        self.target = {}

        for i in range(len(self.init_market)):
            self.param[self.init_market[i]] = self.william_param(self.init_market[i])
            self.target[self.init_market[i]] = self.target_price(self.param[self.init_market[i]], self.init_market[i])

        # 메세징
        ex = self.manager.client.EXCHANGE
        on_time = datetime.datetime.now().strftime('%Y-%m-%d')
        account = self.manager.MANAGER_ALGO_RUN[William.ALGO][ex]
        param = self.param
        target = self.target

        msg = {
            "EX": ex,
            "Time": on_time,
            "Algo": William.ALGO,
            "Balance": account,
            "Param": param,
            "Target": target
        }

        self.send_msg(msg)

        # 재개
        self._run = True

    # 현재가 > 타겟가 매수
    def algo_william(self, money):
        for i in range(len(self.run_market)):
            market = self.run_market[i]
            # 업비트 매수 시
            if self.manager.client.EXCHANGE == "UB":
                try:
                    current_price = self.manager.client.get_current_price(market)[0]['price']

                except Exception as e:
                    print(e)
                else:
                    if current_price >= self.target[market]:
                        order_id = self.manager.client.new_order(market, 'bid', 'limit', money=money,
                                                                 target=self.target[market])

                        self.order_id.append(order_id)

                        # 매수정보 입력#@#@#@#

                        self.run_market.remove(market)
                        break

            # 바이낸스 매수 시
            elif self.manager.client.EXCHANGE == "BN":
                try:
                    order_id = self.manager.client.new_order(market, "BUY", "STOP_LOSS_LIMIT", money=money,
                                                             target=self.target[market])
                    print(order_id)

                    # orderdata.txt 로 파일 입력
                    ####

                    self.order_id.append(order_id)
                    self.run_market.remove(market)
                    break
                except Exception as e:
                    print(e)

    # 파라미터 계산함수 이거 좀더 최적화 시켜볼것
    def william_param(self, market):
        data = self.manager.client.get_day_candle(market, self.data_amount)
        data.reverse()
        data.pop()

        beta = {}
        sharp = {}

        # 파라미터 0.5 미만은 미리 제거
        for par in range(50):
            parameter = (99 - par) / 100
            profit = []
            for i in range(len(data) - 1):

                prev_high = data[i]['high_price']
                prev_low = data[i]['low_price']
                prev_close = data[i]['trade_price']  # 금일 시작가와도 동일

                today_high = data[i + 1]['high_price']
                today_close = data[i + 1]['trade_price']

                buying_price = prev_close + (prev_high - prev_low) * parameter
                today_profit = 0
                if buying_price <= today_high:
                    today_profit = ((today_close - buying_price) / buying_price) - self.fee

                # 하루 수익
                profit.append(today_profit)

            # 현재 파라미터에 대한 표준편차
            stdev = numpy.std(profit, ddof=1)
            period = len(data)
            beta_param = round(stdev * numpy.sqrt(period), 5)
            sharp_param = round(numpy.average(profit) * period / beta_param, 5)

            # 파라미터 키에 따라 베타 값 벨류로 딕셔너리 생성
            beta[str(round(parameter, 2))] = beta_param
            sharp[str(round(parameter, 2))] = sharp_param

        # 최적 파라미터 값
        optimal_parameter = max(sharp.items(), key=operator.itemgetter(1))[0]
        return float(optimal_parameter)

    # 매수가 결정함수
    def target_price(self, param, market):
        day_before_data = self.manager.client.get_day_candle(market, 2)[1]
        close = float(day_before_data["trade_price"])
        high = float(day_before_data["high_price"])
        low = float(day_before_data["low_price"])

        target_Price = close + (high - low) * param
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
