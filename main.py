import argparse
import os
import re
from pathlib import PurePath
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise (requests.HTTPError)


def download_txt(url, file_path):
    response = requests.get(f"{url}")
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return
    with open(file_path, 'wb') as file:
        file.write(response.content)


def clear_name(filename):
    filename = re.sub("[\\\\/\\xa0:]", "", filename)
    return filename


def get_book_parameters(url):
    response = requests.get(f"{url}")
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    header = soup.find('h1').text
    header = header.split("::")
    author = header[1]
    title = header[0]
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


def download_book(url, id, book_path='book', image_path='image'):
    if not os.path.exists(book_path):
        os.makedirs(book_path)
    if not os.path.exists(image_path):
        os.makedirs(image_path)

    try:
        author, title, book_url, image_url, *other = get_book_parameters(url)

        if book_url:
            base_url = urlparse(url)
            base_url = f'{base_url.scheme}://{base_url.netloc}'
            download_txt(f'{base_url}/{book_url}',
                         PurePath(book_path, f'{id}. {clear_name(author)} - {clear_name(title)}.txt'))
            if image_url:
                download_txt(f'{base_url}/{image_url}',
                             PurePath(image_path, f'{id}. {clear_name(author)} - {clear_name(title)}.jpg'))
    except requests.HTTPError:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser("download book from tululu.org")
    parser.add_argument('-sid', '--start_id', help='id of start book', default=0, type=int)
    parser.add_argument('-eid', '--end_id', help='id of end book', default=1, type = int)
    parser.add_argument('-b_path', '--book_path', help="path to save book default=book", default='book')
    parser.add_argument('-i_path', '--image_path', help="path to save images, default = images", default='images')
    args = parser.parse_args()
    for i in range(args.start_id, args.end_id+1):
        download_book(f'https://tululu.org/b{i}/', i, book_path=args.book_path, image_path=args.image_path)
