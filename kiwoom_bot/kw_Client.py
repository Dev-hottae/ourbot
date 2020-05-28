from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

from kiwoom_bot.config.errorCode import errors


class Kw_Client(QAxWidget):
    EXCHANGE = "KW"

    DEFAULT_UNIT = 'KRW'

    # 체크할것
    TR_FEE = 0
    MIN_UNIT = 1

    def __init__(self):
        super().__init__()

        ### eventloop 모음##############################
        self.login_event_loop = QEventLoop()
        self.detail_account_info_event_loop = QEventLoop()
        self.get_day_candle_data_loop = QEventLoop()
        self.data_request_loop = QEventLoop()
        ######################################################

        # 로그인 관련부분
        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_commConnect()

        # 계좌정보
        self.account_data = []
        self.account_info()
        print("정상")
        print(len(self.account_data))
        print(self.account_data)

        # 봉데이터
        self.data_box = []
        aa = self.get_day_candle("005300", 2)
        print("aa")
        print(aa)


        # 주문정보
        self.yesterday_uid = []
        self.total_ordered_uid = []

    def event_slots(self):
        # 이벤트 커넥트 데이터 수신
        self.OnEventConnect.connect(self.login_slot)
        # TR 데이터 수신
        self.OnReceiveTrData.connect(self.trdata_slot)

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect")
        self.login_event_loop.exec_()

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
                data = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, cnt, param[key_list[i]])
                data_keeper[key_list[i]] = data
            res.append(data_keeper)
        return res

    ### 데이터 송수신 관련함수
    # 현재 계정 데이터 요청
    def account_info(self, sPrevNext=0):
        # 계좌번호 호출
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")
        account_num = account_list.split(';')[0]

        # 8130731611
        print("my account : ", account_num)

        query = {
            "계좌번호": account_num,
            "비밀번호": "0000",
            "비밀번호매체구분": "00",
            "조회구분": "1",
            "sPrevNext": sPrevNext,
            "rqname": "account_details",
            "key_code": "opw00018"
        }

        self.data_request(query)

    # 일단위 캔들요청
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
    def get_current_price(self, code):
        pass


    # 주문함수
    def new_order(self):
        '''
        "market": res['symbol'],
        "side": res['side'],
        "ord_type": res['type'],
        "ord_price": excuted_price,
        "ord_volume": ord_volume,
        "uuid": res['orderId']
        :return:
        '''
        pass

    def query_order(self):
        '''
        "market": res['symbol'],
        "side": res['side'],
        "ord_type": res['type'],
        "status": res["status"],
        "uuid": res['orderId'],
        "ord_price": req[0]['ord_price'],
        "ord_volume": req[0]['ord_volume'],
        "executed_volume": res["executedQty"]
        :return:
        '''
        pass

    def cancel_order(self):
        pass
    #
    # def get_code_list(self):
    #     '''
    #           [시장구분값]
    #       0 : 장내
    #       10 : 코스닥
    #       3 : ELW
    #       8 : ETF
    #       50 : KONEX
    #       4 :  뮤추얼펀드
    #       5 : 신주인수권
    #       6 : 리츠
    #       9 : 하이얼펀드
    #       30 : K-OTC
    #     '''
    #     code_list = self.get_code_list_by_market("8")
    #     print(len(code_list))
    #
    #     for idx, code in enumerate(code_list):
    #
    #         print("%s  %s : KOSDAQ Stock Code : %s is updating..." % (idx+1, len(code_list), code))
    #         self.day_kiwoom_db(code=code)



    # 데이터 처리
    # OnEventConnect 받는 부분
    def login_slot(self, errCode):
        print("user login : ", errors(errCode))
        self.login_event_loop.exit()

    # OnReceiveTrData 받는 부분
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

        if sRQName == "account_details":
            print(sPrevNext)

            # 계좌 내 보유 종목 수
            cnts = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print(cnts)

            query = {
                "code": "종목번호",
                "stock_name": "종목명",
                "stock_quantity": "보유수량",
                "buying_price": "매입가",
                "current_price": "현재가",
                "cnts": cnts,
                "sTrCode": sTrCode,
                "sRQName": sRQName
            }

            res = self.data_get(query)

            # 데이터 전처리

            for i in range(len(res)):
                code = res[i]['code'].strip()
                stock_name = res[i]['stock_name'].strip()
                stock_quantity = int(res[i]['stock_quantity'].strip())
                buying_price = int(res[i]['buying_price'].strip())
                current_price = int(res[i]['current_price'].strip())

                data_dict = {
                    "market": code,
                    "stock_name": stock_name,
                    "stock_quantity": stock_quantity,
                    "buying_price": buying_price,
                    "current_price": current_price
                }

                if sPrevNext == 2:
                    self.account_info(sPrevNext)
                self.account_data.append(data_dict)

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

            self.data_box = day_candle_data

            self.data_request_loop.exit()



