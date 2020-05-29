import numpy
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import QTest

from kiwoom_bot.config.errorCode import *
from kiwoom_bot.config.kiwoomType import *


class Kw_Client(QAxWidget):
    EXCHANGE = "KW"

    DEFAULT_UNIT = 'KRW'

    # 체크할것
    TR_FEE = 0.00015
    MIN_UNIT = 1

    def __init__(self):
        super().__init__()
        ### 특별변수
        self.W1_data_amount_for_param = 365
        ######################################################
        ### eventloop 모음##############################
        self.login_event_loop = QEventLoop()
        self.detail_account_info_event_loop = QEventLoop()
        self.get_day_candle_data_loop = QEventLoop()
        self.data_request_loop = QEventLoop()
        self.order_request_loop = QEventLoop()
        ######################################################

        ### screen number ####
        self.screen_start_stop_real = "1"
        self.screen_new_order = "1000"
        ######################################################

        ### 외부클래스 파일 객체화
        self.realtype = RealType()
        ######################################################

        ### data box
        self.data_box = []
        self.account_data_box = []
        ######################################################

        # 로그인 관련부분
        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_commConnect()

        # 계좌정보
        # 8130731611
        self.account_num = ""
        account = self.account_info()
        print(account)

        # 주문정보
        self.yesterday_uid = []
        self.total_ordered_uid = []

        # 실시간 수신 관련 함수
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '',
                         self.realtype.REALTYPE['장시작시간']['장운영구분'], "0")

    def event_slots(self):
        # 이벤트 커넥트 데이터 수신
        self.OnEventConnect.connect(self.login_slot)
        # TR 데이터 수신
        self.OnReceiveTrData.connect(self.trdata_slot)
        # Order 데이터 수신
        self.OnReceiveChejanData.connect(self.chejan_slot)

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect")
        self.login_event_loop.exec_()

    def order_request(self, param):

        sRQName = param['sRQName']
        sScreenNo = param['sScreenNo']
        sAccNo = param['sAccNo']
        nOrderType = param['nOrderType']
        sCode = param['sCode']
        nQty = param['nQty']
        nPrice = param['nPrice']
        sHogaGb = param['sHogaGb']

        # 주문요청
        order_req = self.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, ""])

        return order_req

    def data_request(self, param):
        rqname = param.pop("rqname")
        key_code = param.pop('key_code')
        sPrevNext = param.pop("sPrevNext")
        keys = list(param.keys())

        for i in range(len(param)):
            self.dynamicCall("SetInputValue(QString, QString)", keys[i], param[keys[i]])

        # 키 이외의 파라미터 확인할 것
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, key_code, sPrevNext,
                         "2000")

        self.data_request_loop.exec_()

    def data_get(self, param):

        cnts = param.pop("cnts")
        sTrCode = param.pop("sTrCode")
        sRQName = param.pop("sRQName")
        key_list = list(param.keys())
        res = []

        for cnt in range(cnts):
            data_keeper = {}
            for i in range(len(key_list)):
                data = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, cnt,
                                        param[key_list[i]])
                data_keeper[key_list[i]] = data
            res.append(data_keeper)
        return res

    def order_data_request(self, param):

        data_dict = {}
        param_keys = list(param.keys())
        for i in range(len(param)):
            data = self.dynamicCall("GetChejanData(int)", param[param_keys[i]])
            data_dict[param_keys[i]] = data.strip()

        return data_dict

    ### 데이터 송수신 관련함수#############################################
    # 현재 계정 데이터 요청
    def account_info(self, sPrevNext=0):
        # 계좌번호 호출
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")
        self.account_num = account_list.split(';')[0]

        query = {
            "계좌번호": self.account_num,
            "비밀번호": "0000",
            "비밀번호매체구분": "00",
            "조회구분": "1",
            "sPrevNext": sPrevNext,
            "rqname": "account_details",
            "key_code": "opw00018"
        }

        self.data_request(query)

        data = self.data_box[:]

        return data

    # 일단위 캔들요청
    # 600개면 충분할듯
    def get_day_candle(self, code, count, sPrevNext="0"):

        query = {
            "종목코드": code,
            "기준일자": None,
            "수정주가구분": "1",
            "sPrevNext": sPrevNext,
            "rqname": "get_day_candle",
            "key_code": "opt10081"
        }

        self.data_request(query)
        data = self.data_box[:count]

        return data

    # 현재가 호출
    def get_current_price(self, code, sPrevNext="0"):
        query = {
            "종목코드": code,
            "sPrevNext": sPrevNext,
            "rqname": "get_current_data",
            "key_code": "opt10001"
        }

        self.data_request(query)
        data = self.data_box[:]

        # api 요청 빠르게하면 중간에 중단됨
        QTest.qWait(1000)
        return data

    # 주문함수
    def new_order(self, market, side, ord_type, quantity, price=0):
        '''
        시장가, 최유리지정가, 최우선지정가, 시장가IOC, 최유리IOC, 시장가FOK, 최유리FOK, 장전시
        간외, 장후시간외 주문시 주문가격을 입력하지 않습니다.
        '''

        query = {
            "sRQName": "req_new_order",
            "sScreenNo": self.screen_new_order,
            "sAccNo": self.account_num,
            "nOrderType": self.realtype.SENDTYPE['주문유형'][side],
            "sCode": market,
            "nQty": quantity,
            "nPrice": price,
            "sHogaGb": self.realtype.SENDTYPE['거래구분'][ord_type]
        }

        res = self.order_request(query)

        if res == 0:
            print("주문요청 성공")
            self.order_request_loop.exec_()
        else:
            print("주문 실패")

        res = self.data_box[:]

        return res

    # 미체결 조회
    def query_order(self, sPrevNext='0'):

        query = {
            "계좌번호": self.account_num,
            "전체종목구분": 0,
            "매매구분": 0,  # 0:전체, 1:매도, 2:매수
            "체결구분": 1,  # 0:전체, 2:체결, 1:미체결
            "sPrevNext": sPrevNext,
            "rqname": "req_query_order",
            "key_code": "opt10075"
        }

        self.data_request(query)
        data = self.data_box

        return data

    # 이건 필요없을 듯
    def cancel_order(self):
        pass

    #
    def get_code_list(self, market_code):
        '''
              [시장구분값]
          0 : 장내
          10 : 코스닥
          3 : ELW
          8 : ETF
          50 : KONEX
          4 :  뮤추얼펀드
          5 : 신주인수권
          6 : 리츠
          9 : 하이얼펀드
          30 : K-OTC
        '''

        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(';')[:-1]
        return code_list

    # 데이터 처리
    # OnEventConnect 받는 부분
    def login_slot(self, errCode):
        print("user login : ", errors(errCode))
        self.login_event_loop.exit()

    # OnReceiveTrData 받는 부분
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

        if sRQName == "account_details":

            # 계좌 내 보유 종목 수
            cnts = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            query = {
                "code": "종목번호",
                "stock_name": "종목명",
                "stock_quantity": "보유수량",
                "buying_price": "매입가",
                "current_price": "현재가",
                "unlocked": "매매가능수량",
                "cnts": cnts,
                "sTrCode": sTrCode,
                "sRQName": sRQName
            }

            res = self.data_get(query)

            # 데이터 전처리
            for i in range(len(res)):
                code = res[i]['code'].strip()[1:]
                stock_name = res[i]['stock_name'].strip()
                stock_quantity = int(res[i]['stock_quantity'].strip())
                buying_price = int(res[i]['buying_price'].strip())
                current_price = int(res[i]['current_price'].strip())
                unlocked = int(res[i]['unlocked'].strip())

                ### 타 클라이언트와 키값이 달라.... 일단은 코인 잔고 키값으로 통일
                data_dict = {
                    "currency": code,
                    "stock_name": stock_name,
                    "balance": stock_quantity,
                    "locked": stock_quantity - unlocked,
                    "buying_price": buying_price,
                    "current_price": current_price
                }

                self.account_data_box.append(data_dict)
            if sPrevNext == "2":
                self.account_info(sPrevNext)

            else:
                self.data_box = self.account_data_box[:]
                self.account_data_box.clear()
                self.data_request_loop.exit()

        elif sRQName == "get_day_candle":
            # 봉데이터 갯수 // 600개
            cnts = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            query = {
                "market": "종목코드",
                "candle_date_time_kst": "일자",
                "opening_price": "시가",
                "high_price": "고가",
                "low_price": "저가",
                "trade_price": "현재가",
                "candle_acc_trade_price": "거래대금",
                "cnts": cnts,
                "sTrCode": sTrCode,
                "sRQName": sRQName
            }

            res = self.data_get(query)

            # 데이터 전처리
            day_candle_data = []

            for i in range(len(res)):
                market = res[i]['market'].strip()
                candle_date_time_kst = res[i]['candle_date_time_kst'].strip()
                opening_price = int(res[i]['opening_price'].strip())
                high_price = int(res[i]['high_price'].strip())
                low_price = int(res[i]['low_price'].strip())
                trade_price = int(res[i]['trade_price'].strip())
                candle_acc_trade_price = int(res[i]['candle_acc_trade_price'].strip())

                data_dict = {
                    "market": market,
                    "candle_date_time_kst": candle_date_time_kst,
                    "opening_price": opening_price,
                    "high_price": high_price,
                    "low_price": low_price,
                    "trade_price": trade_price,
                    "candle_acc_trade_price": candle_acc_trade_price
                }
                day_candle_data.append(data_dict)

            self.data_box = day_candle_data[:]

            self.data_request_loop.exit()

        elif sRQName == "get_current_data":

            query = {
                "market": "종목코드",
                "stock_name": "종목명",
                "price": "현재가",
                "cnts": 1,
                "sTrCode": sTrCode,
                "sRQName": sRQName
            }

            res = self.data_get(query)

            # 데이터 전처리
            current_data = []

            market = res[0]['market'].strip()
            stock_name = res[0]['stock_name'].strip()
            price = numpy.abs(int(res[0]['price'].strip()))

            data_dict = {
                "market": market,
                "stock_name": stock_name,
                "price": price
            }
            current_data.append(data_dict)

            self.data_box = current_data[:]
            self.data_request_loop.exit()

        elif sRQName == "req_query_order":

            # ordered data 갯수
            cnts = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            print("req_query_order 데이터 갯수", cnts)

            query = {
                "market": "종목코드",
                "stock_name": "종목명",
                "side": "주문구분",
                "ord_type": "매매구분",
                "status": "주문상태",
                "uuid": "주문번호",
                "ord_price": "주문가격",
                "ord_volume": "주문수량",
                "executed_volume": "체결량",
                "cnts": cnts,
                "sTrCode": sTrCode,
                "sRQName": sRQName
            }

            res = self.data_get(query)

            # 데이터 전처리
            query_order_data = []

            for i in range(len(res)):
                market = res[i]['market'].strip()
                stock_name = res[i]['stock_name'].strip()
                side = res[i]['side'].strip()
                ord_type = res[i]['ord_type'].strip()
                status = res[i]['status'].strip()
                uuid = res[i]['uuid'].strip()
                ord_price = int(res[i]['ord_price'].strip())
                ord_volume = int(res[i]['ord_volume'].strip())
                executed_volume = int(res[i]['executed_volume'].strip())

                data_dict = {
                    "market": market,
                    "stock_name": stock_name,
                    "side": side,
                    "ord_type": ord_type,
                    "status": status,
                    "uuid": uuid,
                    "ord_price": ord_price,
                    "ord_volume": ord_volume,
                    "executed_volume": executed_volume
                }
                query_order_data.append(data_dict)

            self.data_box = query_order_data[:]
            # if sPrevNext == "2":
            #     self.query_order(sPrevNext)

            self.data_request_loop.exit()

        else:
            print(sRQName)
            pass

    def chejan_slot(self, sGubun, nItemCnt, sFidList):

        # 주문체결
        if int(sGubun) == 0:

            order_fin = self.realtype.REALTYPE['주문체결']

            req = {
                "market": order_fin['종목코드'],
                "stock_name": order_fin['종목명'],
                "side": order_fin['주문구분'],
                "ord_type": order_fin['매매구분'],
                "ord_price": order_fin['주문가격'],
                "ord_volume": order_fin['주문수량'],
                "uuid": order_fin['주문번호'],
                "status": order_fin['주문상태']
            }

            order_data = self.order_data_request(req)
            self.data_box = [order_data]

            self.order_request_loop.exit()

        elif sGubun == 1:
            print(nItemCnt)
            print(sFidList)
