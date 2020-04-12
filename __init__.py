# -*- coding: utf-8 -*-
import threading
import telegram

from ub_main import *

# 스레드를 통해 여러 프로그램 동시 실행
if __name__ == "__main__":
    # 텔레그램 메시지 봇 on
    tg_bot = telegram.Bot(token=tg_token)

    # 업비트 알고리즘 런
    t2 = threading.Thread(target=ub_Main, args=(tg_bot,))
    t2.start()

