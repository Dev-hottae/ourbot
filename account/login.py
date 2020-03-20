import os
import jwt
import uuid
import hashlib

from account import keys
from urllib.parse import urlencode

import requests

def account_info():
    access_key = keys.access_key
    secret_key = keys.secret_key
    server_url = 'https://api.upbit.com'

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    res = requests.get(server_url + "/v1/accounts", headers=headers)
    return res
