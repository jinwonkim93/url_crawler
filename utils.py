from time import time
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import asyncio
import re

def scrape_image(doc):
    images = [dict(img.attrs)['src']
        for img in doc.html.body.findAll('img',{"src":True})]

    if images:
        return images[0]

    return ''

def scrape_title(doc):
    return doc.html.head.title.text

def scrape_description(doc):
    tag = doc.html.head.findAll('meta', attrs={"name":"description"})
    result = "".join([t['content'] for t in tag])
    return result

def og_valid(dict):
    required_attrs = ['title', 'type', 'image', 'url', 'description']
    return all([ attr in dict.keys() for attr in required_attrs])

def check_url(url):
    result = urlparse(url)
    if result.scheme == '': return False
    else: return True

def check_valid_href(href):
    if len(href) == 0: return False #빈 url 처리
    elif href[0] == '#': return False # #으로된 url처리
    elif href[:10] == 'javascript': return False
    else: return True


def get_href(soup, url):
    sub_url_list = []
    for inner_link in soup.findAll("a"):
        if 'href' in inner_link.attrs:
            sub_href = inner_link.attrs['href']
            if check_valid_href(sub_href):
                if check_url(sub_href):
                    sub_url_list.append(sub_href)
                else:
                    sub_url_list.append(urljoin(url,sub_href))
    return sub_url_list

def get_og(soup,url):
    required_attrs = ['title', 'image', 'description']
    ogs = soup.findAll(property=re.compile(r'^og'))
    dict = {}
    for og in ogs:
        if og.has_attr('content'):
            dict[og['property'][3:]]=og['content']
        if og_valid(dict):        
            return dict
        else:
            temp_dict = {}
            temp_dict['temp_image'] = scrape_image(soup)
            temp_dict['temp_title'] = scrape_title(soup)
            temp_dict['temp_description'] = scrape_description(soup)

            for attr in required_attrs:
                if attr not in dict.keys():
                    dict[attr] = temp_dict['temp_{}'.format(attr)]
            return dict
            
 