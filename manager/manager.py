import time
from urllib.request import urlopen

from apscheduler.schedulers.background import BackgroundScheduler

from bs4 import BeautifulSoup

from account.keys import tg_my_id


# 달러/원 환율 크롤러
from database.datafunc import add_data


def cur_rate():
    html = urlopen("https://finance.yahoo.com/quote/KRW=X?p=KRW=X")

    bsObject = BeautifulSoup(html, "html.parser")
    bsObject = bsObject.find('div', {'id': "quote-header-info"}).find('span', {'data-reactid': '14'}).text
    bsObject = bsObject.replace(",", "")

    return float(bsObject)


class Manager:
    THREADING = False
    INITIAL_TIME = 13
    # [ub_client, bn_client]
    CLIENT = []

    # [ub_manager, bn_manager]
    MANAGER = []
    # {"UB":{"BTC":0.00021, "ETH":0.033}, "BN":{"BTC":0.00011, "ETH":0.0011}}
    MANAGER_ACCOUNT = {}

    # {"UB":212121, "BN":111113}
    MANAGER_TOTAL_MONEY = {}
    MANAGER_MONEY_AVAIL = {}

    # 현재 돌아가는 알고리즘
    # EX {"william" : {"UB": 100, "BN":13}, "onepercent": {"UB": 3000}}
    MANAGER_ALGO_RUN = {}
    MANAGER_ALGO = {}

    def __init__(self, client):
        # 혹여나 거래소 구분이 필요할까 하여 (UPBIT, BINANCE 두가지 존재)
        '''
        exchanges
        1. UB
        2. BN
        '''
        self.exchange = client.EXCHANGE
        self.client = client
        self.usd_rate = 0

        # 등록
        # 클라이언트 관리자
        Manager.CLIENT.append(self.client)

        # 매니저 관리자
        Manager.MANAGER.append(self)
        Manager.MANAGER_ALGO[self.exchange] = 0

        # 잔액관리
        self.having_asset = self.m_account_bal()
        Manager.MANAGER_ACCOUNT[self.exchange] = self.having_asset

        # 잔고 카운팅 기본단위
        self.total_asset = self.m_cal_balance()
        Manager.MANAGER_TOTAL_MONEY[self.exchange] = self.total_asset

    @classmethod
    def main(cls):

        Manager.initializer()

        sched = BackgroundScheduler()
        sched.start()
        sched.add_job(Manager.initializer, 'cron', hour=Manager.INITIAL_TIME, minute=0, second=0, id="m_initializer")

        # 모니터링

        while True:
            if Manager.THREADING:
                Manager.monitor()
            time.sleep(1)

    @classmethod
    def monitor(cls):
        target = Manager.MANAGER

        for i in range(len(target)):
            mn = target[i]
            # account 모니터
            having_asset = mn.m_account_bal()
            Manager.MANAGER_ACCOUNT[mn.exchange] = having_asset

            # 잔액 모니터
            total_asset = mn.m_cal_balance()
            Manager.MANAGER_TOTAL_MONEY[mn.exchange] = total_asset

    # 매 정시마다 각 알고리즘별 금액세팅 (수익과 위험을 기준으로)
    @classmethod
    def m_set_money(cls):
        # 우선은 잔고대비 99% 를 동등배분
        rebalancing = {}
        # MANAGER_ALGO_MONEY
        ex_list = list(dict.keys(Manager.MANAGER_TOTAL_MONEY))
        print(ex_list)
        for i in range(len(ex_list)):
            ex = ex_list[i]
            rebalancing[ex] = int(Manager.MANAGER_TOTAL_MONEY[ex] * 0.99)

            # 바이낸스 수수료목적 차감
            if ex == "BN":
                rebalancing[ex] -= 5

        return rebalancing

    # 정시 초기화
    @classmethod
    def initializer(cls):

        # 스레드 일시정지
        Manager.THREADING = False
        print("스레드 정지")

        # 리벨런싱
        Manager.MANAGER_MONEY_AVAIL = Manager.m_set_money()

        # 알고리즘별 금액분배
        Manager.allocator()
        # EX {"william" : {"UB": 100, "BN":13}, "onepercent": {"UB": 3000}}
        Manager.MANAGER_ALGO_RUN["william"]['UB'] = Manager.MANAGER_MONEY_AVAIL['UB'] / 2
        Manager.MANAGER_ALGO_RUN["william"]['BN'] = Manager.MANAGER_MONEY_AVAIL['BN']
        Manager.MANAGER_ALGO_RUN["onepercent"]['UB'] = Manager.MANAGER_MONEY_AVAIL['UB'] / 2
        Manager.MANAGER_ALGO_RUN['onepercent']['BN'] = 0

        print(Manager.MANAGER_TOTAL_MONEY)

        # # 전체 잔고금액 데이터화
        # add_data(Manager.MANAGER_TOTAL_MONEY)

        print(Manager.MANAGER_MONEY_AVAIL)
        print(Manager.MANAGER_ALGO_RUN)

        # 스레드 재개
        Manager.THREADING = True
        print("스레드 재개!!")

    @classmethod
    def allocator(cls):
        pass

    # 잔고관리
    def m_account_bal(self):
        account = self.client.account_info()
        account_data = {}
        for i in range(len(account)):
            account_data[account[i]['currency']] = float(account[i]['balance']) + float(account[i]['locked'])

        return account_data

    # 잔고 원화 추정치
    # 수수료 명목으로 bnb 코인 일부분 잔고에서 제외
    def m_cal_balance(self):
        default_unit = self.client.DEFAULT_UNIT
        if default_unit == "KRW":
            currency_rate = 1
        elif default_unit == "USDT":
            # 그냥 에러나면 다른 사이트꺼 한번 받아오는게 안전할듯
            try:
                currency_rate = cur_rate()
            except Exception as e:
                print(e)

        balance = 0
        asset_list = self.having_asset
        key_list = list(asset_list.keys())

        for i in range(len(key_list)):
            ticker = key_list[i]
            if ticker == default_unit:
                balance += float(asset_list[ticker])
            else:
                market = self.m_market(ticker)
                price = float(self.client.get_current_price(market)[0]['price']) * float(asset_list[ticker])

                balance += price
        return balance

    def m_market(self, market):
        if self.exchange == "UB":
            return "KRW-" + market
        elif self.exchange == "BN":
            return market + "USDT"
        else:
            return market

    def m_delete_algo(self, algo_name):
        # self.running_algo.remove(algo_name)
        pass


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