import datetime
import hashlib
import hmac
import time
from decimal import Decimal
from urllib.parse import urlencode

import numpy
import requests
from pytz import timezone

from binance_bot.config.realtype import RealType


class Bn_Client():
    EXCHANGE = "BN"
    HOST = "https://api.binance.com"
    DEFAULT_UNIT = "USDT"

    TR_FEE = 0.0015  # account_info 호출하면 나옴 이후에 변경할 것

    def __init__(self, api_key, sec_key):
        self.A_key = api_key
        self.S_key = sec_key

        self.realtype = RealType()

        # william 알고리즘 위한 데이터세팅
        self.W1_data_amount_for_param = 365

    # My account 데이터 호출
    def account_info(self, recvWindow=60000):
        endpoint = "/api/v3/account"

        query = {
            "recvWindow": recvWindow,
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint

        res = requests.get(url, params=query, headers=header)

        # 리턴할때 버퍼가 작은 듯
        res = res.json()["balances"]
        res = list(filter(lambda x: float(x["free"]) > 0, res))

        res_data = []

        for i in range(len(res)):
            data = {
                'currency': res[i]['asset'],
                'balance': res[i]['free'],
                'locked': res[i]['locked']
            }
            res_data.append(data)

        return res_data

    # 코드리스트 요청
    def get_code_list(self, market_code):
        pass

    # 과거 데이터 호출
    def get_day_candle(self, market, limit, interval="1d"):
        endpoint = "/api/v3/klines"

        query = {
            "symbol": market,
            "interval": interval,
            "limit": limit
        }

        url = Bn_Client.HOST + endpoint

        res = requests.get(url, params=query)
        data = res.json()

        last_data_time = datetime.datetime.fromtimestamp(data[limit - 1][0] / 1000, timezone('UTC')).isoformat()
        on_time = datetime.datetime.now(timezone('UTC')).strftime('%Y-%m-%d')

        timer = 0
        while (on_time not in last_data_time) | (timer <= 10):
            res = requests.get(url, params=query)
            data = res.json()

            last_data_time = datetime.datetime.fromtimestamp(data[limit - 1][0] / 1000, timezone('UTC')).isoformat()

            timer += 1
            time.sleep(1)

        data_list = []

        for i in range(len(data) - 1, -1, -1):
            _time = datetime.datetime.fromtimestamp(data[i][0] / 1000).isoformat()
            open = float(data[i][1])
            high = float(data[i][2])
            low = float(data[i][3])
            close = float(data[i][4])
            vol = float(data[i][5])

            one_data = {
                'market': market,
                "candle_date_time_kst": _time,
                "opening_price": open,
                "high_price": high,
                "low_price": low,
                "trade_price": close,
                "candle_acc_trade_price": vol
            }
            data_list.append(one_data)

        return data_list

    # 현재가 호출
    def get_current_price(self, symbol):
        endpoint = "/api/v3/ticker/price"
        query = {
            "symbol": symbol
        }

        url = Bn_Client.HOST + endpoint

        res = requests.get(url, params=query).json()
        res['market'] = res.pop("symbol")
        data = []
        data.append(res)

        return data

    # 지정가/시장가/스탑리밋 매수 주문함수
    def new_order(self, symbol, side, ordtype, vol=None, money=None, target=None, stoptarget=None, recvWindow=60000):
        endpoint = "/api/v3/order"

        side = self.realtype.ORDER['SIDE'][side]
        ordtype = self.realtype.ORDER['ORDTYPE'][ordtype]

        mpm = self.realtype.ORDER['MPM'][symbol]
        mta = self.realtype.ORDER['MTA'][symbol]

        mpmpos = str('{:f}'.format(mpm)).index('1')-1
        mtapos = str('{:f}'.format(mta)).index('1')-1

        if (target and money) is not None:
            target = round((int(target / mpm) * mpm), mpmpos)
            vol = round(money/target, mtapos)

        elif target is not None:
            target = round((int(target / mpm) * mpm), mpmpos)

        elif ((side == 'BUY') and (money is not None)):
            cur_price = float(self.get_current_price(symbol)[0]['price'])
            vol = round(int((money/cur_price)/mta)*mta, mtapos)

        # 스탑리밋 타겟가격 미제출시 타겟가격과 동일시
        if stoptarget is None:
            stoptarget = target

        if ordtype == "LIMIT":
            query = {
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "timeInForce": "GTC",
                "quantity": vol,
                "price": target,
                "recvWindow": recvWindow,
                "timestamp": int(time.time() * 1000)
            }

        elif ordtype == "MARKET":
            query = {
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": vol,
                "recvWindow": recvWindow,
                "timestamp": int(time.time() * 1000)
            }

        elif ordtype == "STOP_LOSS_LIMIT":
            query = {
                "symbol": symbol,
                "side": side,
                "type": "STOP_LOSS_LIMIT",
                "timeInForce": "GTC",
                "quantity": vol,
                "price": target,
                "stopPrice": stoptarget,
                "newOrderRespType": "FULL",
                "recvWindow": recvWindow,
                "timestamp": int(time.time() * 1000)
            }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint

        res = requests.post(url, params=query, headers=header).json()

        if len(res['fills']) > 0:
            ord_volume = res['origQty']
            excuted_price = round(float(res['cummulativeQuoteQty']) / float(res['origQty']), 2)

        else:
            ord_volume = res['origQty']
            excuted_price = res['price']

        data = []
        data_dict = {
            "market": res['symbol'],
            "side": res['side'],
            "ord_type": res['type'],
            "ord_price": excuted_price,
            "ord_volume": ord_volume,
            "uuid": res['orderId'],
            'created_at': datetime.datetime.fromtimestamp(res['transactTime'] / 1000, timezone('UTC')).isoformat()
        }
        data.append(data_dict)

        return data

    # 개별 주문 조회
    def query_order(self, req, recvWindow=60000):
        endpoint = "/api/v3/order"

        query = {
            "symbol": req[0]['market'],
            "orderId": req[0]['uuid'],
            "recvWindow": recvWindow,
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint
        res = requests.get(url, params=query, headers=header).json()

        data = []
        data_dict = {
            "market": res['symbol'],
            'created_at': datetime.datetime.fromtimestamp(res['time'] / 1000, timezone('UTC')).isoformat(),
            "side": res['side'],
            "ord_type": res['type'],
            "status": res["status"],
            "uuid": res['orderId'],
            "ord_price": req[0]['ord_price'],
            "ord_volume": req[0]['ord_volume'],
            "executed_volume": res["executedQty"]
        }
        data.append(data_dict)

        return data

    # 주문 취소
    def cancel_order(self, req, recvWindow=60000):
        endpoint = "/api/v3/order"

        query = {
            "symbol": req['market'],
            "orderId": req['uuid'],
            "recvWindow": recvWindow,
            "timestamp": int(time.time() * 1000)
        }

        query_string = urlencode(query)

        signature = hmac.new(self.S_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        signature = str(signature.hexdigest())

        query["signature"] = signature

        header = {
            "X-MBX-APIKEY": self.A_key
        }

        url = Bn_Client.HOST + endpoint
        res = requests.delete(url, params=query, headers=header).json()

        return res

