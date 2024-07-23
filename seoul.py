import os
import shutil
import requests
from urllib import parse
from library import Library
from epub import *
from pdf import *

class Seoul(Library):
    THIS_FOLDER = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, type):
        self.type = type

    def set_this_folder(self, download_path):
        self.THIS_FOLDER = os.path.dirname(download_path)

    def get_title_list(self, domain, keyword, provider, type):
        strip_keyword = keyword.replace(' ', '')
        pageCount = 100
        payload = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Accept': 'application/json'
            }
        url = f"{domain}/api/contents/search?libCode=&searchKeyword={parse.quote(strip_keyword)}&searchOption=4&sortOption=1&innerSearchYN=N&innerKeyword=&currentCount=1&pageCount={pageCount}&loanable=&isTotal=true&showType=A&searchCombine=N"
        response = requests.request("GET", url, headers=headers, data=payload)

        list = response.json()['ContentDataList']

        result = []
        for item in list:
            result.append({
                "contentsKey": item['contentsKey'],
                "title": item['title'],
                "author": item['author'],
                "publish_date": item['publishDate'],
                "is_reservable": True,
                "is_downloadable": True,
                "publisher": item['publisher'],
                "image": item['coverUrl'],
                "provider" : provider,
                "type" : type,
            })
        
        return result

    def get_contents_detail(self, book_code):
        payload = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Accept': 'application/json'
            }
        url = f"https://elib.seoul.go.kr/api/contents/{book_code}?contentKey={book_code}"
        response = requests.request("GET", url, headers=headers, data=payload)

        return response.json()['Contents'][0]
    
    def do_epub(self, book_code):
        epub = Epub(self.THIS_FOLDER)

        container_data = epub.get_container_data(book_code)
        if not container_data:
            print('no container_data')
            return
        
        full_path = epub.get_container_detail(container_data)
        if not full_path:
            print('no full_path')
            return

        url_part = 'OEBPS'
        file_name = 'content.opf'
        if '/' in full_path:
            url_part = full_path.split('/')[0]
            file_name = full_path.split('/')[1]

        contents_data = epub.get_contents_data(book_code, full_path)
        if not contents_data:
            print('no contents')
            return

        contents_detail = epub.get_contents_detail(contents_data)
        if not contents_detail:
            print('no contents_detail')
            return

        file_list = contents_detail['file_list']
        book_title = contents_detail['book_title']
        book_title = book_title.replace(';', '')
        book_title = book_title.replace('/', ' ')
        book_title = book_title.replace('\t', ' ')
        book_title = book_title.replace(':', '')

        for file_url in file_list:
            result = epub.download_file(book_code, file_url, book_title, url_part)
            if not result:
                print(f'download failed : {file_url}')

        epub.store_file(f'{book_title}/{url_part}', file_name, contents_data)
        epub.store_file(f'{book_title}/META-INF', 'container.xml', container_data)
        epub.store_file(book_title, 'mimetype', bytes('application/epub+zip', 'utf-8'))

        epub.zipfolder(book_title)

        shutil.rmtree(os.path.join(self.THIS_FOLDER, book_title))

    def do_pdf(self, book_code_data):
        pdf = Pdf(self.THIS_FOLDER)
        res = pdf.get_pdf(book_code_data['contentsKey'])
        book_title_author = f"{book_code_data['title']} - {book_code_data['author']}"
        book_title_author = book_title_author.replace(';', '')
        book_title_author = book_title_author.replace('/', ' ')
        book_title_author = book_title_author.replace('\t', ' ')
        book_title_author = book_title_author.replace(':', '')

        print(f'{book_title_author}.pdf')
        pdf.store_file(f'{book_title_author}.pdf', res)
