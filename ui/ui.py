import sys
import asyncio
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from account.login import *
from multiprocessing import *
import schedule

from market_data.callback_by_data_changed import *
from market_data.market_data import *
from market_data.market_trade import *
from scheduler_test.getData import order

try:
    import thread
except ImportError:
    import _thread as thread


class UI_class(QMainWindow):
    def __init__(self):
        super().__init__()

        # 변수 선언
        self.account_data = None
        self.text_edit_btc = None
        self.text_edit_eth = None
        self.text_edit_bnb = None
        self.code_edit = None
        self.account_data_balance = None
        self.market = ["KRW-BTC", "KRW-ETH"]
        self.current_price_url = "https://api.upbit.com/v1/ticker"
        self.info_url = "https://api.upbit.com/v1/candles/days"
        # 시간 표시기
        self.clock()

        # ui 함수호출
        self.basic_Frame()



    def basic_Frame(self):
        self.setWindowTitle("MyCoinTrader")
        self.setGeometry(100, 100, 1200, 800)

        account_label = QLabel('계좌정보조회: ', self)
        account_label.move(20, 20)

        balance_label = QLabel('My Balance: ', self)
        balance_label.move(900, 20)

        #BTC Label
        BTC = QLabel('BTC', self)
        BTC.move(180, 60)
        # ETH Label
        ETH_label = QLabel('ETH', self)
        ETH_label.move(580, 60)
        # BNB Label
        BNB_label = QLabel('BNB', self)
        BNB_label.move(980, 60)

        # 내 자산 현황 // 변화할때마다 데이터 갱신
        self.account_data = account_info()

        # 평단가 기준화폐 'unit_currency'
        my_balance = self.account_data.json()[0].get('balance')
        my_balance = str(round(float(my_balance), 3))
        main_currency = self.account_data.json()[0].get('currency')
        self.account_data_balance = my_balance + " " + main_currency

        label = QLabel(self.account_data_balance, self)
        label.move(1000, 20)

        # 현재가 QText
        self.text_edit_btc = QTextEdit(self)
        self.text_edit_btc.setGeometry(10, 100, 190, 200)
        self.text_edit_btc.setEnabled(False)

        self.text_edit_eth = QTextEdit(self)
        self.text_edit_eth.setGeometry(410, 100, 190, 200)
        self.text_edit_eth.setEnabled(False)

        self.text_edit_bnb = QTextEdit(self)
        self.text_edit_bnb.setGeometry(810, 100, 190, 200)
        self.text_edit_bnb.setEnabled(False)

        # 현재가 데이터 조회("KRW-BTC", "KRW-ETH") // 멀티스레드
        self.price_helper = Market_datas(self.market, self.current_price_url)
        self.price_helper.finished.connect(self.update_marketdata)
        self.price_helper.start()
        print("이후내용 진행")

        # coin info UI
        self.text_edit_btc_info = QTextEdit(self)
        self.text_edit_btc_info.setGeometry(210, 100, 190, 200)
        self.text_edit_btc_info.setEnabled(False)

        self.text_edit_eth_info = QTextEdit(self)
        self.text_edit_eth_info.setGeometry(610, 100, 190, 200)
        self.text_edit_eth_info.setEnabled(False)

        self.text_edit_bnb_info = QTextEdit(self)
        self.text_edit_bnb_info.setGeometry(1010, 100, 190, 200)
        self.text_edit_bnb_info.setEnabled(False)

        # 매일 오전 9시 info data 갱신
        # self.info_helper = Market_datas(self.market, self.info_url)
        # schedule.every().day.at("09:00").do(self.info_helper.finished.connect(self.about_info))
        # self.info_helper.start()


        # 알고리즘 매수 실행(현재가>목표가)
        # buying_price_holder = callback_by_data_changed()
        # buying_price_holder.callback_by_changed(trade_bid)
        trade_bid(data, parameter)

    def about_info(self, data):


        pass

    def update_marketdata(self, data):
        btc_price = int(data[self.market[0]][0]['trade_price'])
        if btc_price >= buying_price_cal(prev_data, parameter):
            order(market,side,volume,price,ord_type)
        eth_price = int(data[self.market[1]][0]['trade_price'])
        self.text_edit_btc.clear()
        self.text_edit_eth.clear()
        self.text_edit_btc.append("현재가 : %s KRW" %btc_price)
        self.text_edit_eth.append("현재가 : %s KRW" %eth_price)
        QApplication.processEvents()


    # 현재시간 함수
    def clock(self):
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.now_time)


    def now_time(self):
        cur_time = QTime.currentTime()
        str_time = cur_time.toString("hh:mm:ss")
        self.statusBar().showMessage(str_time)

