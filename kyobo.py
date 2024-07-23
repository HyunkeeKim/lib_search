import requests
from html import unescape
from bs4 import BeautifulSoup
from library import Library

class Kyobo(Library):

    def __init__(self, type):
        self.type = type

    def get_title_list(self, domain, keyword, provider, type):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        url = f"{domain}/Kyobo_T3_Mobile/Phone/Main/List_Appendix.asp"
        payload={
            "paging":"1",
            "type": "",
            "keyWord": keyword,
            "sortType":"3",
            "classCode":"",
            "product_cd":"",
            "categoryName":"",
            "borrowRadio":""
        }
        response = requests.post(url, headers=headers, data=payload)
        soup = BeautifulSoup(unescape(response.content.decode("utf-8")), 'xml')
        list_soup = soup.find_all('list')

        result_list = []
        if list_soup:
            for data in list_soup:
                result_list.append({
                    "title": data.find('product_nm_kr').get_text(),
                    "author": data.find('text_author_nm').get_text(),
                    "is_reservable": (int(data.find('license_count').get_text()) - int(data.find('borrow_count').get_text()) > 0),
                    "is_downloadable": False,
                    "publisher": data.find('cp_nm1').get_text(),
                    "publish_date": '',
                    "image": data.find('image').get_text(),
                    "provider" : provider,
                    "type" : type,
                })
        
        return result_list
