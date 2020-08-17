import asyncio

from account.keys import *
from upbit_bot.ub_Client import Ub_Client

ub_client = Ub_Client(ub_access_key, ub_secret_key)
asyncio.run(Ub_Client.w_current_price())