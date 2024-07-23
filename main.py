import concurrent.futures
import logging
from functions import read_file
from library import Library

INPUT_DIALOG = '검색할 책 제목 또는 저자를 입력하세요\n> '
CHOOSE_DIALOG = '다운로드할 항목의 번호를 입력하세요(ex. 1,3,4 또는 1-4) 0은 전체\n> '
config = read_file('config.json')

logging.basicConfig(
    format = '%(asctime)s:%(levelname)s:%(message)s',
    datefmt = '%m/%d/%Y %I:%M:%S %p',
    level = logging.INFO
)

def get_search_list(item, search_keyword):
    if not item['enable']:
        return {}

    library = Library.get_library(item['type'])
    if library:
        return library.get_title_list(item['domain'], search_keyword, item['provider'], item['type'])

    return {}

def get_search_books(search_keyword):
    search_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_search_list, item, search_keyword): item for item in config['providers']}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                search_list.append(future.result())
            except Exception as exc:
                logging.error('%r generated an exception: %s' % (url, exc))

    return search_list

def get_book_code_map(map_by_idx, idx_select):
    idxes = []
    if idx_select == '0':
        idxes = map_by_idx.keys()

    elif ',' in idx_select:
        idxes = idx_select.split(',')

    elif '-' in idx_select:
        idxes = idx_select.split('-')

        if len(idxes) == 2:
            temp_idxes = []
            for i in range(int(idxes[0]), int(idxes[1])+1):
                temp_idxes.append(str(i))
            idxes = temp_idxes
    else:
        idxes.append(idx_select)

    book_code_map = {}
    for id in idxes:
        contentsKey = map_by_idx[id]['contentsKey']
        book_code_map[contentsKey] = map_by_idx[id]
    
    return book_code_map

def download(search_result_map):
    idx_select = input(CHOOSE_DIALOG)
    while not idx_select:
        idx_select = input(CHOOSE_DIALOG)

    book_code_map = get_book_code_map(search_result_map, idx_select)

    library = Library.get_library("SL")

    download_path = config['download_path']
    print(download_path)
    if download_path:
        library.set_this_folder(download_path)
        print(f'IN {library.THIS_FOLDER}')

    for book_code_data in book_code_map.values():
        book_code = book_code_data['contentsKey']
        contents_detail = library.get_contents_detail(book_code)

        if not contents_detail:
            print('no contents_detail')
            continue

        if contents_detail['ownerCode'] == 'OV':
            print('ownerCode OV is not available')
            continue

        contents_file_type = contents_detail['contentsFileType']
        if contents_file_type == '1':
            library.do_epub(book_code)
        elif contents_file_type == '2':
            library.do_pdf(book_code_data)

def main():
    search_books = []
    while not search_books:
        search_keyword = input(INPUT_DIALOG)
        while not search_keyword:
            search_keyword = input(INPUT_DIALOG)

        search_books = get_search_books(search_keyword)

        if not search_books:
            print('검색 결과가 없습니다\n')


    result_list = []
    for sl in search_books:
        result_list.extend(sl)

    result_list = sorted(result_list, key=lambda e: (e['title']))

    provider_name = {}
    for p in config['providers']:
        provider_name[p['provider']] = p['name']

    downloadable_list = []
    reservable_list = []
    non_reservable_list = []
    for data in result_list:
        # is_reservable = "대출가능" if data['is_reservable'] else "대출불가"
        if data['is_downloadable']:
            # downloadable_list.append(data)
            reservable_list.append(data)
        elif data['is_reservable']:
            reservable_list.append(data)
        elif not data['is_reservable']:
            non_reservable_list.append(data)

    search_result_map = {}
    if downloadable_list:
        idx =1
        for data in downloadable_list:
            print(f"[ 다운가능 ][ {idx} ] {data['title']} - {data['author']} [ {config['type_code_name'][data['type']]} ][ {provider_name[data['provider']]} ]")
            search_result_map[str(idx)] = data
            idx += 1
        print()

    if reservable_list:
        for data in reservable_list:
            print(f"[ 대출가능 ] {data['title']} - {data['author']} [ {config['type_code_name'][data['type']]} ][ {provider_name[data['provider']]} ]")
        print()

    if non_reservable_list:
        for data in non_reservable_list:
            print(f"[ 대출불가 ] {data['title']} - {data['author']} [ {config['type_code_name'][data['type']]} ][ {provider_name[data['provider']]} ]")

    if downloadable_list:
        download(search_result_map)



if __name__ == "__main__":
   main()
