import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

class Scrapper(object):
    def __init__(self, page, url):
        self.structured_page = BeautifulSoup(page, features = "html.parser")
        self.url = url
   
    def get_urls(self):
        urls = []
        #all_links = self.structured_page.find_all('a', href=re.compile('/'))
        all_links = self.structured_page.find_all('a', attrs={'href': re.compile("^https?://|^/")})
        #all_links = self.structured_page.find_all('a', "exernal-links")
        for link in all_links:
            address = str(link.get('href'))
            #if address in ["None","#"]: continue
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

