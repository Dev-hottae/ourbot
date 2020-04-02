#
# # 목표 매수가 돌파 시 주문 호출을 위한 함수
# import hashlib
# import uuid
# from urllib.parse import urlencode
#
# import jwt
# import requests
#
# from _main import get_target_price_btc, get_btc
# from account import keys
#
# ordered_uuids = []
# def order_btc():
#     print('btc 주문실행...')
#     access_key = keys.access_key
#     secret_key = keys.secret_key
#     server_url = 'https://api.upbit.com'
#     global money_for_btc
#     query = {
#         'market': "KRW-BTC",
#         'side': "bid",
#         'volume': str(money_for_btc / get_target_price_btc(get_btc())),
#         'price': str(get_target_price_btc(get_btc())),
#         'ord_type': "limit",
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
#     print("res : ", res)
#     # 주문 날리면 uuid 저장
#     ordered_uuids.append(res["uuid"])
#     print(ordered_uuids)
#
# order_btc()
