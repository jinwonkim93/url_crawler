from time import time
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import asyncio
import re
from utils import *
from search_api import *
import queue
"""
urls = ['https://namu.wiki/w/%EB%A7%8C%EB%91%90',
        'https://dictionary.cambridge.org/ko/%EC%82%AC%EC%A0%84/%EC%98%81%EC%96%B4/bombard']
"""
 
async def fetch(url):
    try:
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})    # UA가 없으면 403 에러 발생
        response = await loop.run_in_executor(None, urlopen, request)    # run_in_executor 사용
        soup = await loop.run_in_executor(None, BeautifulSoup, response, "html.parser")       # run in executor 사용
        
    except Exception as ex: # 에러 종류
        print('에러가 발생 했습니다', ex)
        await asyncio.sleep(1.0)
    
    return [get_href(soup,url),get_og(soup,url)]
 
async def main():
    result = get100results('사과')
    urls = [ result[i]['link'] for i in range(len(result))]
    url_list = []
    q = queue.Queue()
    q.put(urls)
    while True:
        urls = q.get()
        futures = [asyncio.ensure_future(fetch(url)) for url in urls]
                                                            # 태스크(퓨처) 객체를 리스트로 만듦
        results = await asyncio.gather(*futures)                # 결과를 한꺼번에 가져옴
        
        for res in results:
            print(res)
            #if res == None: continue
            #sub_urls, data = res
            #q.put(sub_urls)
            #url_list.append(data)
        #if len(url_list) > 10: break
        break
    #print(data)



    
 
begin = time()
loop = asyncio.get_event_loop()          # 이벤트 루프를 얻음
loop.run_until_complete(main())          # main이 끝날 때까지 기다림
loop.close()                             # 이벤트 루프를 닫음
end = time()
print('실행 시간: {0:.3f}초'.format(end - begin))