# -*- coding: utf-8 -*-
import sys
import threading

# 스레드를 통해 여러 프로그램 동시 실행
from PyQt5.QtWidgets import QApplication
from account.keys import *
from algoset.larry_williams import William
from algoset.one_percent import One_percent
from binance_bot.bn_Client import *
from kiwoom_bot.kw_Client import Kw_Client
from manager.manager import Manager
from time_checker import time_checker
from upbit_bot.ub_Client import Ub_Client

if __name__ == "__main__":
    '''
    들어가야 하는 내용
    1. manager.py 파일 생성
    2. 매니저 클래스 객체 생성(잔고관리, 통합관리 등을 위함)
    3. 매니저 객체에 각 거래소 객체 연결
    4. 하나의 스레드는 거래소객체와 알고리즘 하나로 구성됨
    5. 정기적으로 각 알고리즘별 수익 체크 및 리벨런싱 진행
    6. 
    '''
    # 서버시간 체크
    time_checker()

    # upbit 객체
    print("클라이언트 생성")
    ub_client = Ub_Client(ub_access_key, ub_secret_key)
    # binance 객체
    bn_client = Bn_Client(bn_access_key, bn_secret_key)
    # 주식 프로그램 객체
    app = QApplication(sys.argv)
    # kw_client = Kw_Client()
    print("클라이언트 완료")

    # # 매니저 관리 프로그램 on
    print("매니저등록 시작")
    ub_manager = Manager(ub_client)
    bn_manager = Manager(bn_client)
    # kw_manager = Manager(kw_client)
    print("매니저등록 완료")

    print("알고리즘 등록")
    # 변동성전략 등록
    # # 업비트 변동성돌파전략
    ub_will = William(ub_manager, ["KRW-BTC", "KRW-ETH"])
    # 바이낸스 변동성돌파전략
    bn_will = William(bn_manager, ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
    # 키움 변동성돌파전략
    # kw_will = William(kw_manager, ['069500', '122630', '233740', '114800', '229200', '133690'])
    # 업비트 원퍼센트 전략 등록
    ub_one = One_percent(ub_manager, ["KRW-ADA", "KRW-BCH", "KRW-EOS", "KRW-ETC", "KRW-XLM", "KRW-TRX", "KRW-XRP"])
    print("알고리즘 등록 완료")
    # 매니저 run

    managing = threading.Thread(target=Manager.main, args=())
    managing.start()
    print("매니저 가동")

    # 알고리즘 start
    # ub_will.start()
    # bn_will.start()
    # kw_will.start()
    ub_one.start()
    print("알고리즘 가동")


    # # 키움 변동성돌파전략
    # kw_will = William(kw_manager, ["069500"])
    # print(kw_will.param)
    # print(kw_will.target)
    # kw_william = threading.Thread(target=kw_will.main, args=())
    # kw_william.start()
    app.exec_()

    ## 추후에는 전체 알고리즘 관리하는 함수 만들고 수익에 따라 할당 Balance 조정
