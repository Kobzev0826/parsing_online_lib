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


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


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

        if not book_url:
            return
        base_url = urlparse(url)
        book_download_link = f'{base_url.scheme}://{base_url.netloc}/{book_url}'
        book_download_path =PurePath(book_path, f'{book_id}. {clear_name(author)} - {clear_name(title)}.txt')
        download_txt(book_download_link, book_download_path)
        if not image_url:
            return

        book_image_download_url = f'{base_url.scheme}://{base_url.netloc}/{image_url}'
        book_image_download_path = PurePath(image_path, f'{book_id}. {clear_name(author)} - {clear_name(title)}.jpg')
        download_txt(book_image_download_url,book_image_download_path)

    except requests.HTTPError:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser("download book from tululu.org")
    parser.add_argument('-sid', '--start_id', help='id of start book', default=1, type=int)
    parser.add_argument('-eid', '--end_id', help='id of end book', default=3, type = int)
    parser.add_argument('-b_path', '--book_path', help="path to save book default=book", default='book')
    parser.add_argument('-i_path', '--image_path', help="path to save images, default = images", default='images')
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id+1):
        download_book(f'https://tululu.org/b{book_id}/', book_id, book_path=args.book_path, image_path=args.image_path)
