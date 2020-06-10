# 환율 크롤러
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup


def cur_rate_google():
    # url = 'https://api.exchangeratesapi.io/latest?base=USD'
    url = 'https://www.google.com/search?q=usdkrw'
    res = requests.get(url)
    print(res)
    bs = BeautifulSoup(res.text, 'html.parser')
    # print(bs)
    cur = bs.select('div#knowledge-currency__updatable-data-column')
    print(cur)
    return float(0)


cur_rate_google()