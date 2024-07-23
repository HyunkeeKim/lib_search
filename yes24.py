import requests
from urllib import parse
from bs4 import BeautifulSoup
from library import Library

class Yes24(Library):

    def __init__(self, type):
        self.type = type

    def get_title_list(self, domain, keyword, provider, type):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ko;q=0.7'
        }

        keyword = keyword.encode('utf-8')
        url = f"{domain}/search/?srch_order=total&src_key={parse.quote(keyword)}"
        response = requests.get(url, headers=headers)
        result = response.content.decode('utf-8')

        soup = BeautifulSoup(result, 'html.parser')
        items = soup.select('div.ebook-list > div.bx > div.info')

        result_list = []
        for item in items:
            title = item.find('p', {'class': 'tit'}).find('a').get_text()
            author = item.find('p', {'class': 'writer'}).get_text()

            detail_spans = item.find('p', {'class', 'detail'}).find_all("span")
            publisher = detail_spans[0].text
            publishDate = detail_spans[1].text
            publishDate = publishDate.replace('-', '/')

            image = item.parent.find('img')['src']

            stat = item.find('div', {'class', 'stat'}).find_all("strong")
            reserve = int(stat[0].text)
            borrow = int(stat[1].text)

            result_list.append({
                "title": title,
                "author": author,
                "is_reservable": (reserve - borrow > 0),
                "is_downloadable": False,
                "publisher": publisher,
                "publish_date": publishDate,
                "image": image,
                "provider" : provider,
                "type" : type,
            })

        return result_list
