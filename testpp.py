import requests


def get_current_price():
    url = "http://www.opinet.co.kr/api/avgAllPrice.do"
    query = {
        "code": 'F788200612',
        'out': 'json'
    }

    res = requests.post(url, params=query).json()


    return res


pp = get_current_price()
print(pp)