from lxml import html
import requests
from pprint import pprint
from datetime import date
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import hashlib



client = MongoClient('127.0.0.1', 27017)
db = client['newsDB']
# db.drop_collection(db.news)
newsDB = db.newsDB


h = hashlib.new('sha256')

url = 'https://yandex.ru/news/'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) /'
                         'AppleWebKit/537.36 (KHTML, like Gecko) /'
                         'Chrome/101.0.4951.67 Safari/537.36'}

response = requests.get(url, headers=headers)

dom = html.fromstring(response.text)
# Собираем топ-5 новостей с Яндекса. Главная новость отличается от 4х остальных, поэтому схожих узлов не так много:(
news = dom.xpath("//section[contains(@aria-labelledby, 'top-heading')]//h2[contains(@class, 'mg-card__title')]")

top_news = []
for el in news:
    news_info = {}

    # Извлекаем заголовок новости, неразрывные пробелы заменяем обычными
    name = el.xpath(".//a/text()")
    name[0] = name[0].replace('\xa0', ' ')

    # Извлекаем ссылку на новость
    link = el.xpath(".//a/@href")

    # Извлекаем источник. На Яндексе он представлен в явном виде,
    # но главная новость отличается от остальных, схожих тегов повыше не нашлось,
    # пришлось много раз подниматься вверх
    source = el.xpath("./../../..//a[@class='mg-card__source-link']/text()")

    # В топе новости только сегодняшние, поэтому дату берём на сегодняшний день, а время - из новости
    date_time = el.xpath("./../../..//span[@class='mg-card-source__time']/text()")
    today = date.today().strftime("%d/%m/%Y")
    date_time.insert(0, today)
    # Собираем всё в один список
    news_info['name'] = name
    news_info['link'] = link
    news_info['source'] = source
    news_info['date_time'] = date_time
    top_news.append(news_info)

# pprint(top_news)

# Добавляем полученные данные в БД:
def db_update(database, news_list):

    for n in news_list:
        try:
            # Генерируем id по заголовку, т.к. некоторые параметры в ссылке
            # на одну и ту же новость меняются со временем => новость может добавиться много раз,
            # а заголовки вряд ли будут одинаковыми у разных новостей
            b_name = bytes(n['name'][0], 'utf-8')
            h.update(b_name)
            _id = h.hexdigest()
            database.insert_one({'_id': _id, **n})
        except DuplicateKeyError:
            print('The news has already been added to database.')


db_update(newsDB, top_news)
#
# for i in newsDB.find({}):
#     pprint(i)
