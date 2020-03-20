import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests

from account import keys


def order(market,side,volume,price,ord_type):
    access_key = keys.access_key
    secret_key = keys.secret_key
    server_url = 'https://api.upbit.com'

    query = {
        'market': market,
        'side': side,
        'volume': volume,
        'price': price,
        'ord_type': ord_type,
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    print(res.text)


get_url = "https://api.upbit.com/v1/candles/days"
querystring_BTC = {"market":"KRW-BTC","count":"2","convertingPriceUnit":"KRW"}
querystring_ETH = {"market":"KRW-ETH","count":"2","convertingPriceUnit":"KRW"}




def get_btc():
    response_krw = requests.request("GET", get_url, params=querystring_BTC)
    prev_data_json = response_krw.json()[1]
    print(str(prev_data_json))


def get_eth():
    response_krw = requests.request("GET", get_url, params=querystring_ETH)
    prev_data_json = response_krw.json()[1]