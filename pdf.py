import requests
import os

class Pdf():
    def __init__(self, THIS_FOLDER):
        self.THIS_FOLDER = THIS_FOLDER

    
    def store_file(self, file_name, data):
        download_file_path = os.path.join(self.THIS_FOLDER, file_name)
        with open(download_file_path, 'wb') as f:
            f.write(data)


    def get_pdf(self, book_code):
        url = f"https://elib.seoul.go.kr/pdf/{book_code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Referer': f'https://elib.seoul.go.kr/PDFViewer/web/viewer.html?contentKey={book_code}'
        }

        res = requests.get(url, headers=headers)

        if not res.content:
            print(f"[{res.status_code}]{res.content}")
            return

        return res.content
