import requests
import ssl
import json
import urllib.request
from urllib import parse
from library import Library

class Bookcube(Library):

    def __init__(self, type):
        self.type = type

    def get_title_list(self, domain, keyword, provider, type):
        url = f"{domain}/FxLibrary/m/product/productSearch/?category=&sort=3&keyword={parse.quote(keyword)}&keyoption2=&page=1"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        request = urllib.request.Request(url, headers=headers)

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        response = urllib.request.urlopen(request, context=context)
        response_data = response.read().decode('utf-8')
        json_data = json.loads(response_data)

        result_list = []
        success = json_data['success']
        result = json_data['result']

        if success:
            for data in result[1]:

                result_list.append({
                    "title": data['title'],
                    "author": data['author'],
                    "is_reservable": data['is_reservable'],
                    "is_downloadable": False,
                    "publisher": data['publisher'],
                    "publish_date": data['publish_date'],
                    "image": data['detail_image'],
                    "provider" : provider,
                    "type" : type,
                })
        
        return result_list
