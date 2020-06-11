import json

import requests


def cur_rate_sub():
    url = 'https://api.exchangeratesapi.io/latest?base=USD'

    res = requests.get(url).text
    res = json.loads(res)['rates']['KRW']
    res = round(res, 2)
    print(res)
    return res

cur_rate_google()