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

# List of servers in order of attempt of fetching
server_list = ['time.windows.com']

'''
Returns the epoch time fetched from the NTP server passed as argument.
Returns none if the request is timed out (5 seconds).
'''
def gettime_ntp(addr='time.windows.com'):
    # http://code.activestate.com/recipes/117211-simple-very-sntp-client/
    TIME1970 = 2208988800      # Thanks to F.Lundh
    client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    data = '\x1b' + 47 * '\0'
    data = data.encode()
    try:
        # Timing out the connection after 5 seconds, if no response received
        client.settimeout(5.0)
        client.sendto(data, (addr, 123))
        data, address = client.recvfrom( 1024 )
        if data:
            epoch_time = struct.unpack( '!12I', data )[10]
            epoch_time -= TIME1970
            return epoch_time
    except socket.timeout:
        return None

if __name__ == "__main__":
    # Iterates over every server in the list until it finds time from any one.
    for server in server_list:
        epoch_time = gettime_ntp(server)
        if epoch_time is not None:
            # SetSystemTime takes time as argument in UTC time. UTC time is obtained using utcfromtimestamp()
            utcTime = datetime.datetime.utcfromtimestamp(epoch_time)
            win32api.SetSystemTime(utcTime.year, utcTime.month, utcTime.weekday(), utcTime.day, utcTime.hour, utcTime.minute, utcTime.second, 0)
            # Local time is obtained using fromtimestamp()
            localTime = datetime.datetime.fromtimestamp(epoch_time)
            print("Time updated to: " + localTime.strftime("%Y-%m-%d %H:%M") + " from " + server)
            break
        else:
            print("Could not find time from " + server)