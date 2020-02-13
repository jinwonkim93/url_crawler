import aiohttp
import asyncio
from urllib.request import urlopen, Request
from Scrapper import Scrapper
from get_domain import get_domain_name
from reppy.robots import Robots
from urllib.parse import urlparse, urljoin

class URLoader(object):
    def __init__(self, session):
        self.hdr = {'User-Agent': 'keyword_bot'}
        self.session = session
    
    def is_robot_valid(self, url):
        robot_url = urljoin(get_domain_name(url), "robots.txt")
        rp = Robots.fetch(robot_url)
        yield rp.allowed(url, self.hdr['User-Agent'])
    
    async def fetch(self,url):
        with aiohttp.Timeout(1):
            async with self.session.get(url) as response:
                assert response.status == 200
                return await response.read()
                
        

    async def open_page(self, url):
        page = await self.fetch(url)
        return Scrapper(page, url)
