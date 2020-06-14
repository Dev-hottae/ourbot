import copy
import datetime
import operator
import threading
import time

import numpy
import pandas as pd
import telegram
from apscheduler.schedulers.background import BackgroundScheduler

from account.keys import *
from database.datafunc import load_data, del_data, add_data
from manager.manager import Manager


# 스레드락
class William(threading.Thread):
    ALGO = "william"
    DATAROAD = './database/data_will.csv'

    def run(self):

        # 스케쥴러 등록
        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(self.initializer, 'cron', hour=Manager.INITIAL_TIME, minute=0, second=0, id="will_initializer")

        while True:
            Manager.LOCK.acquire()
            if (Manager.THREADING and self._run) is True:
                # 알고리즘에 금액할당
                money_alloc = Manager.MANAGER_ALGO_RUN[William.ALGO][self.manager.client.EXCHANGE]
                money = money_alloc / len(self.init_market)
                self.algo_william(money)
                self.live_check("will run")
            else:
                print("Will 스레드 일시정지")
            time.sleep(1)
            Manager.LOCK.release()

    # William(ub_manager, ["KRW-BTC", "KRW-ETH"])
    def __init__(self, manager, market):

        threading.Thread.__init__(self)
        self.msg_bot = telegram.Bot(token=tg_token)

        self._run = True
        self.manager = manager
        self.fee = self.manager.client.TR_FEE

        # 매니저에 알고리즘 등록
        Manager.MANAGER_ALGO_RUN[William.ALGO] = copy.deepcopy(Manager.MANAGER_ALGO)

        # ["KRW-BTC", "KRW-ETH"]
        self.init_market = market[:]
        self.run_market = []
        self.data_amount = self.manager.client.W1_data_amount_for_param

        # 파라미터 초기화
        self.param = {}
        self.target = {}

        # 나머지 초기화
        self.initializer()

    # 매 정시 파라미터 타겟 가격 초기화
    def initializer(self):
        Manager.LOCK.acquire()
        self._run = False
        print("Will 스레드 정지")

        # 데이터 로드
        print("전일 데이터 로드")
        order_data = load_data(self.manager, William.DATAROAD)
        print(order_data)

        # 전일 보유물량 매도
        if len(order_data) > 0:
            for i in range(len(order_data)):
                req = order_data[i]
                # 매수주문요청된 거래들 취소
                if (req["status"] == "NEW") or (req["status"] == "wait"):
                    try:
                        cancel = self.manager.client.cancel_order(req)
                        print("전일매수 주문요청거래 취소")
                    except Exception as e:
                        print(e)
                    else:
                        del_data(req, William.DATAROAD)
                        print("DB에서 삭제")
                else:
                    # 매수시행된 주문 매도
                    try:
                        sell = self.manager.client.new_order(req['market'], 'ask', 'market', vol=req['executed_volume'])
                        print("전일 매수자산 매도")
                    except Exception as e:
                        print(e)
                    else:
                        while True:
                            try:
                                res = self.manager.client.query_order(sell)[0]
                                if (res['status'] != 'wait') and (res['status'] != 'NEW'):
                                    print("매도진행중")
                                    del_data(req, William.DATAROAD)
                                    print("DB에서 삭제")
                                    break
                            except:
                                print("자산 매도 주문 쿼리 실패 & 재요청")
                                time.sleep(1)

        self.run_market = self.init_market[:]

        # 파라미터 초기화
        self.param = {}
        self.target = {}

        for i in range(len(self.init_market)):
            self.param[self.init_market[i]] = self.william_param(self.init_market[i])
            self.target[self.init_market[i]] = self.target_price(self.param[self.init_market[i]], self.init_market[i])

        print("WILL 마켓, 파라미터 ,타겟가격 초기화")

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

        print("Will 메시지 전송", msg)

        self.send_msg(msg)

        # 재개
        self._run = True
        print("Will 스레드 재가동")
        Manager.LOCK.release()

    # 현재가 > 타겟가 매수
    def algo_william(self, money):
        for i in range(len(self.run_market)):
            market = self.run_market[i]
            # 업비트 매수 시
            if self.manager.client.EXCHANGE == "UB":
                try:
                    current_price = self.manager.client.get_current_price(market)[0]['price']
                    print(market, " 현재가: ", current_price, " 타겟: ", self.target[market])
                except Exception as e:
                    print("UB 현재가 받아오기 실패", e)
                else:
                    if current_price >= self.target[market]:
                        # 나중을 위해 limit 주문인데 만약 일부만 체결이되면?
                        order_id = self.manager.client.new_order(market, 'bid', 'price', money=money)
                        print("will 매수진행", market)
                        # 매수정보 입력
                        info = self.manager.client.query_order(order_id)
                        add_data(info, William.DATAROAD)
                        print("DB 데이터입력")

                        self.run_market.remove(market)
                        break

            # 바이낸스 매수 시
            elif self.manager.client.EXCHANGE == "BN":
                try:
                    order_id = self.manager.client.new_order(market, "bid", "stop_loss_limit", money=money,
                                                             target=self.target[market])
                except Exception as e:
                    print("BN 스탑리밋 주문실패", e)
                else:
                    print("Will BN 스탑리밋 주문성공")
                    print(order_id)
                    # 매수주문정보 입력
                    while True:
                        try:
                            info = self.manager.client.query_order(order_id)
                        except Exception as e:
                            print(e, "request again")
                            time.sleep(1)
                        else:
                            break
                    add_data(info, William.DATAROAD)
                    print("DB 데이터입력")

                    self.run_market.remove(market)
                    break

    # 파라미터 계산함수 이거 좀더 최적화 시켜볼것
    def william_param(self, market):
        while True:
            try:
                data = self.manager.client.get_day_candle(market, self.data_amount)
            except Exception as e:
                print("파라미터 계산용 데이터 수신 실패", e)
            else:
                if len(data) > 150:
                    break
                time.sleep(1)

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

    def live_check(self, name):
        _time = int(datetime.datetime.now().timestamp())
        # 10분간격 확인
        if (_time % 600) < 5:
            print(name)

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
