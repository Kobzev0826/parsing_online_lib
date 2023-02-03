import argparse
import os,re, sys
from pathlib import PurePath
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import time


def get_response(url):
    flag = True
    start_time = time.time()
    while flag:
        try:
            response = requests.get(url)
            flag = False
        except requests.ConnectionError:
            if time.time() - start_time > 300:
                sys.exit("no connection for more than 5 minutes")
            time.sleep(1)
    return response


def check_for_redirect(response):
    if response.history:
        raise (requests.HTTPError)


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_content_in_file(url, file_path):
    response = get_response(f"{url}")
    response.raise_for_status()

    check_for_redirect(response)

    with open(file_path, 'wb') as file:
        file.write(response.content)


def clear_name(filename):
    filename = re.sub("[\\\\/\\xa0:]", "", filename)
    return filename


def get_book_parameters(url):
    response = get_response(f"{url}")
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    title, author, *other = soup.find('h1').text.split('::')
    genres = soup.find('span', class_="d_book").find('a').text

    comments = []
    for comment in soup.find_all('div', class_='texts'):
        comments.append(comment.find('span').text)

    image = soup.find('div', class_='bookimage').find('a').find('img')
    if image:
        image_url = image['src']

    book_url = soup.find('a', title=re.compile('txt'))
    if book_url:
        book_url = book_url['href']

    return author, title, book_url, image_url, comments, genres


def download_book(url, book_id, book_path='book', image_path='image'):
    check_dir(book_path)
    check_dir(image_path)

    try:
        author, title, book_url, image_url, *other = get_book_parameters(url)
    except requests.HTTPError:
        print(f"redirect in link {url}", file=sys.stderr)
        return

    if not book_url:
        print(f"no book to link {url}", file=sys.stderr)
        return


    book_download_link = urljoin(url, book_url)
    book_download_path =PurePath(book_path, f'{book_id}. {clear_name(author)} - {clear_name(title)}.txt')
    try:
        download_content_in_file(book_download_link, book_download_path)
    except requests.HTTPError:
        print(f"redirect in link {book_download_link}", file=sys.stderr)
        return

    if not image_url:
        print(f"no image link {url}", file=sys.stderr)
        return

    book_image_download_url = urljoin(url,image_url)
    book_image_download_path = PurePath(image_path, f'{book_id}. {clear_name(author)} - {clear_name(title)}.jpg')
    try:
        download_content_in_file(book_image_download_url,book_image_download_path)
    except requests.HTTPError:
        print(f"redirect in link {book_image_download_url}", file=sys.stderr)
        return




if __name__ == '__main__':
    parser = argparse.ArgumentParser("download book from tululu.org")
    parser.add_argument('-sid', '--start_id', help='id of start book', default=1, type=int)
    parser.add_argument('-eid', '--end_id', help='id of end book', default=3, type = int)
    parser.add_argument('-b_path', '--book_path', help="path to save book default=book", default='book')
    parser.add_argument('-i_path', '--image_path', help="path to save images, default = images", default='images')
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id+1):
        download_book(f'https://tululu.org/b{book_id}/', book_id, book_path=args.book_path, image_path=args.image_path)
