import re
#from urllib.request import urlopen, Request
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import queue
import time

from get_domain import *
from reppy.robots import Robots
from search_api import *
import asyncio
from functools import partial
import aiohttp

class URLoader(object):
    def __init__(self, session):
        self.hdr = {'User-Agent': 'keyword_bot'}
        self.session = session
    
    def is_robot_valid(self, url):
        robot_url = urljoin(get_domain_name(url), "robots.txt")
        rp = Robots.fetch(robot_url)
        yield rp.allowed(url, '*')
    
    async def fetch(self,url):
        #loop = asyncio.get_event_loop()
        #req = await loop.run_in_executor(None, partial(Request,headers=self.hdr), url)
        #res = await loop.run_in_executor(None,partial(urlopen, timeout=0.3), req)
        #return res

        with aiohttp.Timeout(1):
            async with self.session.get(url) as response:
                assert response.status == 200
                return await response.read()
                
        

    async def open_page(self, url):
        page = await self.fetch(url)
        return Scrapper(page, url)


class Scrapper(object):
    def __init__(self, page, url):
        self.structured_page = BeautifulSoup(page, features = "html.parser")
        self.url = url
   
    def get_urls(self, url):
        urls = []
        #all_links = self.structured_page.find_all('a', href=re.compile('/'))
        all_links = self.structured_page.find_all('a', "exernal-links")
        for link in all_links:
            address = str(link.get('href'))
            if address in ["None","#"]: continue
            if not urlparse(address).netloc:
                scheme = urlparse(url).scheme
                base_url = urlparse(url).netloc
                address = ''.join([scheme, '://', base_url, address])
            urls.append(address)
        return urls
    
    def get_graph(self):
        """
        get beautifulsoup
        return og dict
        """
        required_attrs = ['title', 'image', 'description', 'url']
        ogs = self.structured_page.find_all(property=re.compile(r'^og'))
        dict = {}
        for og in ogs:
            if og.has_attr('content'):
                dict[og['property'][3:]]=og['content']
            
            if self._is_og_valid(dict):        
                return dict
            else:
                temp_dict = self.get_body_graph()
                for attr in required_attrs:
                    if attr not in dict.keys():
                        dict[attr] = temp_dict['temp_{}'.format(attr)]
                return dict

    def get_body_graph(self):
        dict = {}
        dict['temp_image'] = self._scrape_image()
        dict['temp_title'] = self._scrape_title()
        dict['temp_description'] = self._scrape_description()
        dict['temp_url'] = self.url
        return dict

    def _scrape_image(self):
        images = [dict(img.attrs)['src']
            for img in self.structured_page.html.body.find_all('img',{"src":True})]

        if images:
            return images[0]

        return ''

    def _scrape_title(self):
        return self.structured_page.html.head.title.text

    def _scrape_description(self):
        tag = self.structured_page.html.head.find_all('meta', attrs={"name":"description"})
        result = "".join([t['content'] for t in tag])
        return result
    

    def _is_og_valid(self, dict):
        required_attrs = ['title', 'type', 'image', 'url', 'description']
        return all([ attr in dict.keys() for attr in required_attrs])



class Main_crawler(object):
    def __init__(self, urloader):
        self.urloader = urloader
        self.queue = queue.Queue()
        self.db = []
        self.master_set = set([])

    
    def _is_url_visited(self, url):
        if url in self.master_set:
            return True
        else:
            self.master_set.add(url)
            return False
    
    def save(self, graph):
        if graph == None: return
        self.db.append(graph)

    def queue_all(self, items):
        [self.queue.put(item) for item in items]

    async def crawl_from_queue(self, limit):
        while not self.queue.empty() and len(self.db) <= limit:
            url = self.queue.get()
            if not self._is_url_visited(url):
                try:
                    if self.urloader.is_robot_valid(url):
                        scrapper = await self.urloader.open_page(url)
                        urls = scrapper.get_urls(url)
                        graph = scrapper.get_graph()
                        self.save(graph)
                        self.queue_all(urls)
                except Exception as ex: # 에러 종류
                    print('에러가 발생 했습니다', ex)

        

def start_crawling(links):
    start = time.time()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    hdr = {'User-Agent': 'keyword_bot'}
    with aiohttp.ClientSession(headers=hdr, loop=loop) as session:
        url_loader = URLoader(session)
        main_crawler = Main_crawler(url_loader)
        main_crawler.queue_all(links)
        loop.run_until_complete(main_crawler.crawl_from_queue(100))
        print(main_crawler.db)
        print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
        loop.close()
        return main_crawler.db

"""
if __name__ == '__main__':
    main()

"""