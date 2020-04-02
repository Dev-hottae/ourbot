import numpy
import operator

def param(data):
    data.reverse()
    trading_fee = 0.002     # 서비스마다 다름

    beta = {}
    sharp = {}

    # 파라미터 0.5 미만은 미리 제거
    for par in range(50):
        parameter = (99-par)/100
        profit = []
        for i in range(len(data)-1):

            prev_high = data[i]['high_price']
            prev_low = data[i]['low_price']
            prev_close = data[i]['trade_price']   # 금일 시작가와도 동일

            today_high = data[i+1]['high_price']
            today_close = data[i+1]['trade_price']

            buying_price = prev_close + (prev_high - prev_low) * parameter
            today_profit = 0
            if buying_price <= today_high:
                today_profit = ((today_close - buying_price)/buying_price) - trading_fee

            # 하루 수익
            profit.append(today_profit)
            
        # 현재 파라미터에 대한 표준편차
        stdev = numpy.std(profit, ddof=1)
        period = len(data)
        beta_param = round(stdev * numpy.sqrt(period), 5)
        sharp_param = round(numpy.average(profit) * period / beta_param, 5)

        # 파라미터 키에 따라 베타 값 벨류로 딕셔너리 생성
        beta[str(round(parameter,2))] = beta_param
        sharp[str(round(parameter,2))] = sharp_param

    # 최적 파라미터 값
    optimal_parameter = max(sharp.items(), key=operator.itemgetter(1))[0]
    return float(optimal_parameter)



# testing
# param(eth_data)