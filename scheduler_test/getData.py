# import os
# import jwt
# import uuid
# import hashlib
# from urllib.parse import urlencode
#
# from account import keys
# import requests
# import sys
#
# def ask():
#     access_key = keys.access_key
#     secret_key = keys.secret_key
#     server_url = 'https://api.upbit.com'
#
#     query = {
#         'state': 'wait',
#     }
#     query_string = urlencode(query)
#
#     uuids_query_string = '&'.join(["uuids[]={}".format(uuid) for uuid in uuids])
#
#     query['uuids[]'] = uuids
#     print("middle check")
#     print(query['uuids[]'])
#     if len(query['uuids[]'])==0:
#         return
#     query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()
#
#     m = hashlib.sha512()
#     m.update(query_string)
#     query_hash = m.hexdigest()
#
#     payload = {
#         'access_key': access_key,
#         'nonce': str(uuid.uuid4()),
#         'query_hash': query_hash,
#         'query_hash_alg': 'SHA512',
#     }
#
#     jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
#     authorize_token = 'Bearer {}'.format(jwt_token)
#     headers = {"Authorization": authorize_token}
#
#     res = requests.get(server_url + "/v1/orders", params=query, headers=headers)
#     print("현재 주문요청중인 거래")
#     print(res.json())
# uuids = []
#
# def order_btc_for_waiting():
#     print('btc 주문실행...')
#     access_key = keys.access_key
#     secret_key = keys.secret_key
#     server_url = 'https://api.upbit.com'
#
#     query = {
#         'market': 'KRW-BTC',
#         'side': 'bid',
#         'volume': '0.00116928',
#         'price': '900000',
#         'ord_type': 'limit',
#     }
#     query_string = urlencode(query).encode()
#
#     m = hashlib.sha512()
#     m.update(query_string)
#     query_hash = m.hexdigest()
#
#     payload = {
#         'access_key': access_key,
#         'nonce': str(uuid.uuid4()),
#         'query_hash': query_hash,
#         'query_hash_alg': 'SHA512',
#     }
#
#     jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
#     authorize_token = 'Bearer {}'.format(jwt_token)
#     headers = {"Authorization": authorize_token}
#
#     res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
#     res = res.json()
#     print(res)
#     print(type(res))
#     uuids.append(res["uuid"])
#
#
# # order_btc()
# # order_btc()
# # print("현재 주문요청된 거래 : ")
# # print(uuids)
# # print('ask 함수')
# # ask()