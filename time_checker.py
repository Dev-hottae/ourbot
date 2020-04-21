import ntplib

def time_checker():
    timeServer = 'time.windows.com'               # NTP Server Domain Or IP
    c = ntplib.NTPClient()
    response = c.request(timeServer, version=3)
    print('NTP Server Time과 Local Time과 차이는 %.2f s입니다.' %response.offset)
    return 0