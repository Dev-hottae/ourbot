import requests


def area():
    url = "http://www.opinet.co.kr/api/searchByName.do"
    query = {
        "code": 'F788200612',
        'out': 'json',
        'osnm': '서울',
    }

    res = requests.post(url, params=query).json()

    return res
def get_current_price():
    url = "http://www.opinet.co.kr/api/detailById.do"
    query = {
        "code": 'F788200612',
        'out': 'json',
        'id': 'A0016401',
    }

    res = requests.post(url, params=query).json()

    return res

pp = area()
pp = pp['RESULT']['OIL']
print(pp)

dd = get_current_price()
print(dd)

