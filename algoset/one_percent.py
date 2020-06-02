import copy
import datetime
import threading
import time

import pandas as pd
import telegram
from apscheduler.schedulers.background import *

from account.keys import *
from manager.manager import Manager


class One_percent(threading.Thread):
    ALGO = "onepercent"
    DATAROAD = './algoset/orderdata/data_one.csv'

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
        Manager.MANAGER_ALGO_RUN[One_percent.ALGO] = copy.deepcopy(Manager.MANAGER_ALGO)
        # ex ["KRW-BTC", "KRW-ETH"]
        self.init_market = market[:]
        self.run_market = []

        self.money = 0

        # 금일 타겟가
        self.target = {}
        self.sell_target = {}

        # 나머지 초기화
        self.initializer()

    def initializer(self):
        # 초기화 중 알고리즘 잠시 정지
        self._run = False

        # 데이터 로드
        order_data = self.load_data()
        print(order_data)
        # 매도 성사 데이터 삭제
        for_cancel = []
        for i in range(len(order_data)):
            data = order_data[i]
            if (data['status'] == 'NEW') or (data['status'] == 'wait'):
                for_cancel.append(data)
            else:
                self.del_data(data)

        # 매도 실패 물량 주문 취소 및 시장가 매도진행
        # 전일 보유물량 취소 및 매도
        if len(for_cancel) > 0:
            for i in range(len(for_cancel)):
                req = for_cancel[i]
                self.manager.client.cancel_order(req)

                ## 주문취소후 바로 시장가매도 되는지 테스트 필요
                if self.manager.client.EXCHANGE == "UB":
                    self.manager.client.new_order(req['market'], 'ask', 'market', vol=req['executed_volume'])

                elif self.manager.client.EXCHANGE == "BN":
                    self.manager.client.new_order(req["market"], "SELL", "MARKET", vol=req['executed_volume'])
                self.del_data(req)

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

                    # 매수즉시 타겟가로 지정가매도주문
                    while True:
                        info = self.manager.client.query_order(order_id)[0]
                        print(info['status'])
                        if info['status'] != 'wait':
                            break

                    print(info)
                    print(self.sell_target)
                    sell_order = self.manager.client.new_order(market, 'ask', 'limit', vol=info['executed_volume'], target=self.sell_target[market])

                    # 매도주문정보 입력
                    sell_order_id = self.manager.client.query_order(sell_order)
                    self.add_data(sell_order_id)

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

    # pandas data 추가쓰기
    # data 형식 [{"aaa":090}]
    def add_data(self, data):
        df = pd.DataFrame(data)
        # 데이터 로드
        try:
            load = pd.read_csv(One_percent.DATAROAD).to_dict('records')
        except Exception as e:
            df.to_csv(One_percent.DATAROAD, mode='a', header=True, index=False)
        else:
            for i in range(len(load)):
                check = load[i]['uuid']
                # 같은 id 체크
                if check == data[0]['uuid']:
                    return
            df = pd.DataFrame(data)
            df.to_csv(One_percent.DATAROAD, mode='a', header=False, index=False)

    # pasdas data 지우기
    def del_data(self, data):
        try:
            load = pd.read_csv(One_percent.DATAROAD)
        except Exception as e:
            return
        else:
            for i in range(len(load.uuid)):
                if load.uuid[i] == data['uuid']:
                    load = load.drop([load.index[i]])
            # 남은 데이터 새로 쓰기
            load.to_csv(One_percent.DATAROAD, header=True, index=False)

    # pasdas data load
    def load_data(self):
        try:
            # 데이터 로드
            data = pd.read_csv(One_percent.DATAROAD).to_dict('records')
        except Exception as e:
            new_query = []
            print(e)
        else:
            # query order 갱신
            new_query = []
            for i in range(len(data)):
                res = self.manager.client.query_order(data[i])[0]
                new_query.append(res)
        finally:
            return new_query

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
