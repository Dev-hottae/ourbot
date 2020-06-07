import csv
import datetime

import pandas as pd
from pytz import timezone

data = [{"UB":212121, "BN":111114}]
direc ='./database/data_test.csv'
load = pd.read_csv('./database/data_test.csv')
print(load)
_date = datetime.datetime.now(timezone('UTC')).strftime('%Y-%m-%d')
# 오늘날짜가 미기록이면
if _date != load.date[len(load.date) - 1]:
    df = pd.DataFrame(data, index=[_date])
    df.to_csv(direc, mode='a', header=False, index=True)
# 기록이면
else:
    pass
    # ## csv 맨 아랫줄 삭제
    # with open(direc, 'wb') as out:
    #     writer = csv.writer(out)
    #     writer.writerows('')
    # df = pd.DataFrame(data, index=[_date])
    # df.to_csv(direc, mode='a', header=False, index=True)