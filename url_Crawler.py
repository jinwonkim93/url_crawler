import re
import requests
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import queue
import time

from get_domain import *
from reppy.robots import Robots
from search_api import *

class URLoader(object):
    def __init__(self):
        self.hdr = {'User-Agent': 'keyword_bot'}
    
    def is_robot_valid(self, url):
        robot_url = urljoin(get_domain_name(url), "robots.txt")
        rp = Robots.fetch(robot_url)
        yield rp.allowed(url, self.hdr['User-Agent'])
    
    def fetch(self,url):
        #req = Request(url, headers=self.hdr)
        req = requests.get(url, headers=self.hdr)
        return req


    def open_page(self, url):
        page = self.fetch(url)
        return Scrapper(page, url)


class Scrapper(object):
    def __init__(self, page, url):
        #self.structured_page = BeautifulSoup(urlopen(page, timeout=5), features = "html.parser",from_encoding="iso-8859-1")
        self.structured_page = BeautifulSoup(page.text, features = "html.parser")
        self.url = url
   
    def get_urls(self):
        urls = []
        #all_links = self.structured_page.find_all('a', href=re.compile('/'))
        all_links = self.structured_page.find_all('a', attrs={'href': re.compile("^https?://")})
        for link in all_links:
            #print(link)
            address = str(link.get('href'))
            #print(address)
            if not urlparse(address).netloc:
                scheme = urlparse(self.url).scheme
                base_url = urlparse(self.url).netloc
                address = ''.join([scheme, '://', base_url, address])
            urls.append(address)
        return urls
    
    def get_graph(self):
        """
        get beautifulsoup
        return og dict
        """
        required_attrs = ['title', 'image', 'description', 'url']
        ogs = self.structured_page.findAll(property=re.compile(r'^og'))
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
            for img in self.structured_page.html.body.findAll('img',{"src":True})]

        if images:
            return images[0]

        return ''

    def _scrape_title(self):
        return self.structured_page.html.head.title.text

    def _scrape_description(self):
        tag = self.structured_page.html.head.findAll('meta', attrs={"name":"description"})
        result = "".join([t['content'] for t in tag])
        return result
    

    def _is_og_valid(self, dict):
        required_attrs = ['title', 'type', 'image', 'url', 'description']
        return all([ attr in dict.keys() for attr in required_attrs])



class MainCrawler(object):
    def __init__(self, urloader):
        self.urloader = urloader
        self.Queue = queue.Queue()
        self.DB = []
        self.master_set = set([])
    
    def _is_url_visited(self, url):
        if url in self.master_set:
            return True
        else:
            self.master_set.add(url)
            return False
    
    def save(self, graph):
        if graph == None: return
        self.DB.append(graph)

    def queue_all(self, items):
        [self.Queue.put(item) for item in items]

    def crawl_from_queue(self, limit):
        while not self.Queue.empty() and len(self.DB) <= limit:
            url = self.Queue.get()
            if not self._is_url_visited(url):
                try:
                    if self.urloader.is_robot_valid(url):
                        scrapper = self.urloader.open_page(url)
                        if scrapper is None: continue
                        urls = scrapper.get_urls()
                        graph = scrapper.get_graph()
                        self.save(graph)
                        self.queue_all(urls)
                        #print(len(self.DB))
                except Exception as ex: # 에러 종류
                    print('에러가 발생 했습니다', ex)
                    pass
                finally:
                    #time.sleep(1)
                    pass

        

def start_crawl(keyword):
    url_loader = URLoader()
    main_crawler = MainCrawler(url_loader)

    links = get100results(keyword)
    main_crawler.queue_all(links)
    main_crawler.crawl_from_queue(5)
    print("Done!")
    return main_crawler.DB
