import copy
import datetime
import threading
import time

import pandas as pd
import telegram
from apscheduler.schedulers.background import *

from account.keys import *
from database.datafunc import load_data, del_data, add_data
from manager.manager import Manager


class One_percent(threading.Thread):
    ALGO = "onepercent"
    DATAROAD = './database/data_one.csv'

    def run(self):

        # 스케쥴러 등록
        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(self.initializer, 'cron', hour=Manager.INITIAL_TIME, minute=0, second=0, id="one_initializer")

        while True:
            if (Manager.THREADING and self._run) is True:
                # 알고리즘에 금액할당
                money_alloc = Manager.MANAGER_ALGO_RUN[One_percent.ALGO][self.manager.client.EXCHANGE]
                money = money_alloc / len(self.init_market)
                self.algo_onepercent(money)
                self.live_check("one run")
            else:
                print("One 스레드 일시정지 중입니다...")
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
        Manager.MANAGER_ALGO_RUN[One_percent.ALGO] = copy.deepcopy(Manager.MANAGER_ALGO)
        # ex ["KRW-BTC", "KRW-ETH"]
        self.init_market = market[:]
        self.run_market = []

        # 금일 타겟가
        self.target = {}
        self.sell_target = {}

        # 나머지 초기화
        self.initializer()

    def initializer(self):
        # 초기화 중 알고리즘 잠시 정지
        self._run = False
        print("One 스레드 정지")

        # 데이터 로드
        print("전일 데이터 로드")
        order_data = load_data(self.manager, One_percent.DATAROAD)
        print(order_data)
        # 매도 성사 데이터 삭제
        for_cancel = []
        for i in range(len(order_data)):
            data = order_data[i]
            if ((data['status'] == 'NEW') or (data['status'] == 'wait')):
                for_cancel.append(data)
                print("매도실패 주문:", data)
            else:
                del_data(data, One_percent.DATAROAD)
                print("매도성공 주문 DB 삭제:", data)

        # 매도 실패 물량 주문 취소 및 시장가 매도진행
        # 전일 보유물량 취소 및 매도
        if len(for_cancel) > 0:
            print("보유자산의 실패한 매도주문취소를 진행합니다")
            for i in range(len(for_cancel)):
                req = for_cancel[i]
                try:
                    sell = self.manager.client.cancel_order(req)
                except Exception as e:
                    print(e)
                else:
                    check_sell = self.manager.client.query_order([sell])
                    while True:
                        if (check_sell[0]['status'] != 'NEW') and (check_sell[0]['status'] != 'wait'):
                            print("주문 취소 진행 성공")
                            break
                        time.sleep(1)

                    try:
                        self.manager.client.new_order(req['market'], 'ask', 'market', vol=req['executed_volume'])
                        print("주문 취소자산 매도주문 진행")
                    except Exception as e:
                        print(e)
                    else:
                        del_data(req, One_percent.DATAROAD)
                        print("DB 데이터 삭제")

        self.run_market = self.init_market[:]

        # 파라미터 초기화
        self.target = {}
        self.sell_target = {}

        print("ONE 마켓, 타겟가격 초기화")

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

        print("One 메시지 전송", msg)

        self.send_msg(msg)

        # 재개
        self._run = True
        print("One 스레드 재가동")

    # 개별시장마다
    ## 일단 업비트만
    def algo_onepercent(self, money):
        for i in range(len(self.run_market)):
            market = self.run_market[i]
            try:
                current_price = self.manager.client.get_current_price(market)[0]['price']
                print(market, "현재가: ", current_price)
            except Exception as e:
                print("현재가 데이터 수신 실패", e)
            else:
                if current_price >= self.target[market]:
                    print("여기서 자꾸 무슨 키 에러가 발생함::::::", current_price, market, self.target[market])
                    order_id = self.manager.client.new_order(market, 'bid', 'price', money=money,
                                                             target=self.target[market])
                    print(market, "One 매수진행")
                    # 매수즉시 타겟가로 지정가매도주문
                    while True:
                        info = self.manager.client.query_order(order_id)[0]
                        if info['status'] != 'wait':
                            
                            break
                    sell_order = self.manager.client.new_order(market, 'ask', 'limit', vol=info['executed_volume'], target=self.sell_target[market])
                    print(market, "매도주문이 되었습니다")
                    # 매도주문정보 입력
                    sell_order_id = self.manager.client.query_order(sell_order)
                    add_data(sell_order_id, One_percent.DATAROAD)
                    print("DB 에 데이터 저장")

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

    def live_check(self, name):
        _time = int(datetime.datetime.now().timestamp())
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

