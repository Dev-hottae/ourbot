

# pandas data 추가쓰기
# data 형식 [{"aaa":090}]
import datetime

import pandas as pd
from pytz import timezone


def add_m_data(data):
    direc = './database/total_asset.csv'
    load = pd.read_csv(direc)
    _date = datetime.datetime.now(timezone('UTC')).strftime('%Y-%m-%d')

    # 오늘날짜가 미기록이면
    if _date != load.date[len(load.date) - 1]:
        df = pd.DataFrame(data, index=[_date])
        df.to_csv(direc, mode='a', header=False, index=True)
    # 기록이면
    else:
        pass


def add_data(data, direc):
    df = pd.DataFrame(data)
    # 데이터 로드
    try:
        load = pd.read_csv(direc).to_dict('records')
    except Exception as e:
        df.to_csv(direc, mode='a', header=True, index=False)
    else:
        for i in range(len(load)):
            check = load[i]['uuid']
            # 같은 id 체크
            if check == data[0]['uuid']:
                return
        df = pd.DataFrame(data)
        df.to_csv(direc, mode='a', header=False, index=False)

# pasdas data 지우기
def del_data(data, direc):
    try:
        load = pd.read_csv(direc)
    except Exception as e:
        return
    else:
        for i in range(len(load.uuid)):
            if load.uuid[i] == data['uuid']:
                load = load.drop([load.index[i]])
        # 남은 데이터 새로 쓰기
        load.to_csv(direc, header=True, index=False)

# pasdas data load
def load_data(mn, direc):
    try:
        # 데이터 로드
        data = pd.read_csv(direc).to_dict('records')
    except Exception as e:
        new_query = []
        print(e)
    else:
        # query order 갱신
        new_query = []
        for i in range(len(data)):
            res = mn.client.query_order([data[i]])[0]
            new_query.append(res)
    finally:
        return new_query
