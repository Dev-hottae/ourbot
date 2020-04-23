import datetime
import hashlib
import hmac
import time
import uuid
from decimal import Decimal

import jwt
import numpy
from urllib.parse import *

import requests
from pytz import timezone

from account.keys import *
import ntplib
# from time import ctime
#
# timeServer = 'time.windows.com'               # NTP Server Domain Or IP
# c = ntplib.NTPClient()
# response = c.request(timeServer, version=3)
# print('NTP Server Time과 Local Time과 차이는 %.2f s입니다.' %response.offset)

import socket
import struct
import sys
import time
import datetime
import win32api
import subprocess
a = [1,3,4]
b= [5,6,7,8]
a = b
print(a)