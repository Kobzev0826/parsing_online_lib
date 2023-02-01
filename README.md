# parsing_online_lib
Скрипт позволяет скачать книги в формате .txt а так же картинки обложек с сайтa [tululu.org](https://tululu.org/).\
Скачивает подрят книги от `start_id` до `end_id` (см. раздел "Принимаемые параметры")

## Как установить

Python3 уже должен быть установлен.
```
pip install -r requirements.txt
```
Если есть конфликт с python2.
```
pip3 install -r requirements.txt
```
## Как использовать
запустить файл `main.py`\
`python main.py`

### Принимаемые параметры 
- `start_id` id стартовой книги 
- `end_id` id последней книги
- `book_path` относительный путь до директории сохранения книг
- `image_path` относительный путь до директории сохранения изображений обложек
доополнительно можно посмотреть в help вызвав `main.py -h`

### Пример запуска
```
python main.py --start_id=20 --end_id=39
```
