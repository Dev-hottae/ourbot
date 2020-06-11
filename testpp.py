import json
import re

import requests
from bs4 import BeautifulSoup

for day in range(20200501, 20200532):

    page = 0
    react_score = 0
    news_cate_dict = {}

    while True:

        page += 1

        URL = 'https://news.naver.com/main/list.nhn?mode=LPOD&mid=sec&oid=001&date={}&page={}'.format(day, page)

        res = requests.get(URL)
        bs = BeautifulSoup(res.text, 'html.parser')
        # 페이지 체크
        real_page = bs.select('div.paging strong')[0].text

        if page != int(real_page):
            print('page break')
            break
        else:
            news_all = bs.select('div#main_content div.list_body ul li dt.photo')
            for news in news_all:
                news_link = news.select('a')[0].attrs['href']

                news_res = requests.get(news_link)
                news_bs = BeautifulSoup(news_res.text, 'html.parser')

                # 기사타입
                news_type = news_bs.select('div#header span.blind')[1].text

                # 기사본문
                if news_type == '뉴스':
                    news_body = news_bs.select('div#main_content div#articleBodyContents')[0].text.strip().replace("  ","")
                elif news_type == '스포츠':
                    news_body = news_bs.select('div#newsEndContents')[0].text.strip().replace("  ", "")

                news_body = re.sub("(▶.*)","", news_body)

                # 삼성전자 기사만 이후 진행
                if '삼성전자' not in news_body:
                    continue
                else:
                    ######################
                    ### 삼성전자에 관한 기사들
                    # 기사감정
                    news_id = news_link[-10::]
                    react_link = 'https://news.like.naver.com/v1/search/contents?suppress_response_codes=true&q=NEWS%5Bne_001_{0}%5D%7CNEWS_MAIN%5Bne_001_{0}%5D'.format(news_id)

                    react_res = requests.get(react_link).json()['contents'][0]['reactions']
                    react_dict = {}

                    # react 스코어
                    for react in react_res:

                        feel = react['reactionType']
                        if (feel == 'want') or (feel == 'like') or (feel == 'warm'):
                            react_score += 1
                        else:
                            react_score -= 1
                    ###########################
                    # 기사 카테고리
                    try:
                        news_cate = news_bs.select('div.guide_categorization em')[0].text
                    except:
                        news_cate = 'nocate'

                    try:
                        news_cate_dict[news_cate] += 1
                    except KeyError:
                        news_cate_dict[news_cate] = 1


        print(day, page, react_score, news_cate_dict)
