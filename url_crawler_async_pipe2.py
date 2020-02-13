import asyncio, logging
from search_api import get100results as search_keyword
from URLoader import URLoader
import aiohttp
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)


num_workers = 20
num_scrappers = 30

class Web_crawler(object):
    def __init__(self):
        self.db = []
        self.master_set = set([])

    def _is_url_visited(self, url):
        if url in self.master_set:
            return False
        else:
            self.master_set.add(url)
            return True

    async def run(self,keyword):
        self.url_queue = asyncio.Queue()
        self.page_queue = asyncio.Queue()

        #better to use async def
        #for request in search_keyword(keyword):
        #    await self.url_queue.put((request,0))

        tasks = []
            
        for i in range(num_workers):
            tasks.append(asyncio.create_task(
                self.get_page(name=f'get_page-{i}')))
        
        for i in range(num_scrappers):
            tasks.append(asyncio.create_task(self.get_data(name=f'get_data-{i}')))
        
        await self.search_web(keyword)
        await self.url_queue.join()
        await self.page_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        return(self.db)
    
    async def search_web(self, keyword):
        for request in search_keyword(keyword):
            await self.url_queue.put((request,0))
        
    async def get_page(self, name):
        #print(f"{name} started")
        hdr = {'User-Agent': 'keyword_bot'}
        async with aiohttp.ClientSession(headers=hdr) as session:
            url_loader = URLoader(session)
            try:
                while True:
                    url, depth = await self.url_queue.get()
                    try:
                        if depth > 3 or len(self.db) > 5:
                            continue
                        scrapper = await url_loader.open_page(url)
                        await self.page_queue.put(scrapper)
                        await asyncio.sleep(0)
                        urls = scrapper.get_urls()
                        #confirm robots.txt and check if already crawled the urls
                        if url_loader.is_robot_valid(url) and self._is_url_visited(url) :
                            await self.update_get_page(urls,depth)
                    except Exception as e:
                        #print(f"{name} exception {e!r}")
                        continue
                    finally:
                        self.url_queue.task_done()
            except asyncio.CancelledError:
                #print(f"{name} is being cancelled")
                raise
            finally:
                #print(f"{name} ended")
                pass
                

    async def get_data(self, name):
        #print(f"{name} started")
        try:
            while True:
                page = await self.page_queue.get()
                try:
                    graph = page.get_graph()
                    self.save(graph)
                    await asyncio.sleep(0)
                except Exception as e:
                    #print(f"{name} exception {e!r}")
                    raise
                finally:
                    self.page_queue.task_done()
        except asyncio.CancelledError:
            #print(f"{name} is being cancelled")
            raise
        finally:
            #print(f"{name} ended")
            pass

    def save(self, graph):
        if graph == None: return
        self.db.append(graph)
    
    async def update_get_page(self, urls, depth):
        [await self.url_queue.put((url, depth+1)) for url in urls]


def start_crawl(keyword):
    apple_crawler = Web_crawler()
    #result = asyncio.run(apple_crawler.run(keyword), debug=True)
    result = asyncio.run(apple_crawler.run(keyword))
    print('Done!')
    return result
