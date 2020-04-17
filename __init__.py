# -*- coding: utf-8 -*-
import threading

import telegram

# 스레드를 통해 여러 프로그램 동시 실행
from binance_bot.bn_Main import *
from upbit_bot.ub_Main import *

if __name__ == "__main__":
    # 텔레그램 메시지 봇 on
    tg_bot = telegram.Bot(token=tg_token)

    # 업비트 변동성돌파전략
    # bot1 = threading.Thread(target=ub_main, args=(tg_bot,))
    # bot1.start()

    # 바이낸스 변동성돌파전략
    bot2 = threading.Thread(target=bn_main, args=(tg_bot,))
    bot2.start()
    ## 추후에는 전체 알고리즘 관리하는 함수 만들고 수익에 따라 할당 Balance 조정

