import requests
import ssl
import urllib.request
from urllib import parse
from html import unescape
from bs4 import BeautifulSoup
from library import Library

class KyoboNew(Library):

    def __init__(self, type):
        self.type = type

    def get_title_list(self, domain, keyword, provider, type):
        url = f"{domain}/search/searchList.ink?schClst=all&schDvsn=000&orderByKey=&schTxt={parse.quote(keyword)}"

        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT

        response = urllib.request.urlopen(url, context=ctx)
        rsp_text = response.read().decode("utf-8")

        soup = BeautifulSoup(rsp_text, 'html.parser')
        list_soup = soup.select('ul.book_resultList > li')

        result_list = []
        if list_soup:
            for data in list_soup:
                result_list.append({
                    "title": data.find('li', {'class', 'tit'}).find('a').get_text(),
                    "author": data.find('li', {'class', 'writer'}).contents[0].strip(),
                    "is_reservable": data.find('input', {'name':'brwBtn'}) if True else False,
                    "is_downloadable": False,
                    "publisher": data.find('span', {'class', 'store'}).get_text(),
                    "publish_date": '',
                    "image": data.find('div', {'class', 'img'}).find('img')['src'],
                    "provider" : provider,
                    "type" : type,
                })
        
        return result_list
