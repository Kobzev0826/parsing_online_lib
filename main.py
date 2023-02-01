import re, os
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from pathlib import PurePath


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
    print(file_path)
    with open(file_path,'wb') as file:
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
    image = soup.find('div',class_='bookimage').find('a').find('img')
    if image:
        image_url = image['src']
    print(image)
    book_url = soup.find('a',title=re.compile('txt'))
    if book_url:
        book_url = book_url['href']

    return author, title, book_url, image_url


def download_book(url,id, path='book'):
    if not os.path.exists(path):
        os.makedirs(path)
    print(id)
    try:
        author, title, book_url, image_url = get_book_parameters(url)
        if book_url:
            base_url = urlparse(url)
            base_url = f'{base_url.scheme}://{base_url.netloc}'
            download_txt(f'{base_url}/{book_url}',PurePath(path,f'{id}. {clear_name(author)} - {clear_name(title)}.txt'))
            if image_url:
                download_txt(f'{base_url}/{image_url}',
                             PurePath(path, f'{id}. {clear_name(author)} - {clear_name(title)}.jpg'))
    except requests.HTTPError:
        pass

if __name__=='__main__':
    # response = requests.get(f"https://tululu.org/txt.php?id={5}")
    # print(response.history)
    # url = 'https://tululu.org/txt.php?id=1'
    # for i in range(1,11):
    #     download_image(f"https://tululu.org/txt.php?id={i}", f'{i}.txt')
    # response = requests.get(f"https://tululu.org/b5/")
    # for i in range(1,11):
        # download_book(f'https://tululu.org/b{i}/',i)
    download_book(f'https://tululu.org/b{9}/', 9)
    # with open('book/9.   Крейнер Стюарт - Бизнес путь: Джек Уэлч. 10 секретов величайшего в мире короля менеджмента  ','wb') as file:
    #     print('!')
