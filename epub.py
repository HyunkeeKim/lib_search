import requests
import os
from zipfile import ZipFile, ZIP_DEFLATED
from bs4 import BeautifulSoup
from html import unescape

class Epub():
    def __init__(self, THIS_FOLDER):
        self.THIS_FOLDER = THIS_FOLDER

    
    def store_file(self, folder_name, file_name, data):
        title_directory = os.path.join(self.THIS_FOLDER, folder_name)
        if not os.path.exists(title_directory):
            os.makedirs(title_directory)

        folder_name_and_name = os.path.join(folder_name, file_name)
        download_file_path = os.path.join(self.THIS_FOLDER, folder_name_and_name)

        with open(download_file_path, 'wb') as f:
            f.write(data)


    def get_data(self, book_code, url_part):
        url = f"https://elib.seoul.go.kr/epubs/{book_code}/{url_part}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Referer': f'https://elib.seoul.go.kr/EPUBViewer3/index.html?contentKey={book_code}'
        }

        return requests.get(url, headers=headers)


    def download_file(self, book_code, file_url, book_title, url_part):
        res = self.get_data(book_code, f'{url_part}/{file_url}')

        if not res.content:
            print(f"[{res.status_code}]{res.content}")
            return False

        folder_name = f'{book_title}/{url_part}'
        if '/' in file_url:
            file_urls = file_url.split('/')
            folder_name += f'/{file_urls[0]}'
            file_url = file_urls[1]

        print(f'{folder_name}/{file_url}')
        self.store_file(folder_name, file_url, res.content)

        return True


    def get_contents_data(self, book_code, full_path):
        res = self.get_data(book_code, full_path)

        if not res.content:
            print(f"[{res.status_code}]{res.content}")
            return

        return res.content

    def get_container_data(self, book_code):
        res = self.get_data(book_code, 'META-INF/container.xml')

        if not res.content:
            print(f"[{res.status_code}]{res.content}")
            return

        return res.content

    def get_container_detail(self, container_data):
        soup = BeautifulSoup(unescape(container_data.decode("utf-8")), 'xml')

        return soup.find('rootfile')['full-path']

    def get_contents_detail(self, contents_data):
        file_list = []

        soup = BeautifulSoup(unescape(contents_data.decode("utf-8")), 'xml')
        metadata = soup.find('package').find('metadata')
        title = metadata.find('dc:title').get_text()

        creator = ''
        if metadata.find('dc:creator'):
            creator = metadata.find('dc:creator').get_text()

        items = soup.select('manifest > item')
        for item in items:
            file_list.append(item['href'])
        
        return {
            "book_title": f'{title} - {creator}',
            "file_list": file_list
        }

    def zipfolder(self, foldername):
        foldername_with_path = os.path.join(self.THIS_FOLDER, foldername)
        zip_name = foldername + '.epub'
        zip_file_path = os.path.join(self.THIS_FOLDER, zip_name)

        with ZipFile(zip_file_path, 'w', ZIP_DEFLATED) as zip_ref:
            for folder_name, subfolders, filenames in os.walk(foldername_with_path):
                for filename in filenames:
                    file_path = os.path.join(folder_name, filename)
                    zip_ref.write(file_path, arcname=os.path.relpath(file_path, foldername))

        zip_ref.close()

