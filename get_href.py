import re
from urllib.request import urlopen, Request
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from get_domain import *
import time
from reppy.robots import Robots
from og import *
import queue
import time

#http,https 모두 가능

def check_url(url):
    result = urlparse(url)
    if result.scheme == '': return False
    else: return True

def check_valid_href(href):
    if len(href) == 0: return False #빈 url 처리
    elif href[0] == '#': return False # #으로된 url처리
    elif href[:10] == 'javascript': return False
    else: return True

def reppy_robot(url):
    robot_url = urljoin(get_domain_name(url), "robots.txt")
    rp = Robots.fetch(robot_url)
    #print(rp.allowed(href, '*'))
    yield rp.allowed(url, '*')


def get_href_list(linklist):
    try:
        url_list = []
        q = queue.Queue()
        [q.put(x) for x in linklist]
        while q.empty() is not True:
            link = q.get()
            try:
                if not reppy_robot(link): continue
                hdr = {'User-Agent': 'Mozilla/5.0'}
                req = Request(link, headers=hdr)
                soup = BeautifulSoup(urlopen(req), features="html.parser")
                sub_url_list = []
                url_data = dict([])
                #get og
                opengraph = OpenGraph(url=link, scrape=True)
                for x,y in opengraph.items():
                    url_data[x] = y

                #get url
                for inner_link in soup.findAll("a"):
                    if 'href' in inner_link.attrs:
                        sub_href = inner_link.attrs['href']
                        if check_valid_href(sub_href):
                            if check_url(sub_href):
                                sub_url_list.append(sub_href)
                            else:
                                sub_url_list.append(urljoin(link,sub_href))
                
                time.sleep(1)
                url_list.append(url_data)
                if len(sub_url_list) != 0: 
                    #url_list.append(sub_url_list) #아무것도 없으면 안넣음
                    [q.put(x) for x in sub_url_list]
                if len(url_list) > 10: break

            except Exception as ex: # 에러 종류
                print('href 관련 에러가 발생 했습니다', ex)

    
    except Exception as ex: # 에러 종류
        print('에러가 발생 했습니다', ex)
    #print(url_list)  
    return url_list

start = time.time()  # 시작 시간 저장
 
 
 

#a = reppy_robot('https://namu.wiki/', 'https://namu.wiki/w/%EB%A7%8C%EB%91%90')
#if a: print('hi')
list = ['https://namu.wiki/w/%EB%A7%8C%EB%91%90',
        'https://dictionary.cambridge.org/ko/%EC%82%AC%EC%A0%84/%EC%98%81%EC%96%B4/bombard']
print(get_href_list(list))
print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
