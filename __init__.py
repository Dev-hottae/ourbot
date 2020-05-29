# -*- coding: utf-8 -*-
import sys
import threading

# 스레드를 통해 여러 프로그램 동시 실행
from PyQt5.QtWidgets import QApplication

from kiwoom_bot.kw_Client import Kw_Client
from upbit_bot.ub_Main import *

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
    # time_checker()

    # # # upbit 객체
    # ub_client = Ub_Client(ub_access_key, ub_secret_key)
    # #
    # # # binance 객체
    # bn_client = Bn_Client(bn_access_key, bn_secret_key)
    # # # 주식 프로그램 객체
    app = QApplication(sys.argv)
    kw_client = Kw_Client()
    print("클라이언트")

    # # # 매니저 관리 프로그램 on
    # ub_manager = Manager(ub_client)
    # bn_manager = Manager(bn_client)
    kw_manager = Manager(kw_client)
    print("매니저등록완료")
    # # # 매니저 run
    managing = threading.Thread(target=Manager.monitor, args=())
    managing.start()
    # #
    # # # 업비트 변동성돌파전략
    # ub_will = William(ub_manager, ["KRW-BTC", "KRW-ETH"])
    # print(ub_will.param)
    # print(ub_will.target)
    # ub_william = threading.Thread(target=ub_will.main, args=())
    # ub_william.start()
    # #
    # # # 바이낸스 변동성돌파전략
    # bn_will = William(bn_manager, ["BTCUSDT","ETHUSDT","BNBUSDT"])
    # print(bn_will.param)
    # print(bn_will.target)
    # bn_william = threading.Thread(target=bn_will.main, args=())
    # bn_william.start()
    app.exec_()
    while True:
        time.sleep(5)

    ## 추후에는 전체 알고리즘 관리하는 함수 만들고 수익에 따라 할당 Balance 조정
