from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)

db = client['vacDB']
# db.drop_collection(db.vacDB)
vacDB = db.vacDB

# https://hh.ru/search/vacancy?text=Data+scientist&area=1&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=50&no_magic=true&L_save_area=true&from=suggest_post
main_url = 'https://hh.ru'
vacancy = 'Data Scientist'
page = 0
all_vacancies = []
params = {'text': vacancy,
          'area': 2,
          'experience': 'doesNotMatter',
          'order_by': 'relevance',
          'search_period': 0,
          'items_on_page': 19,
          'page': page}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                         'AppleWebKit/537.36 (KHTML, like Gecko)'
                         'Chrome/98.0.4758.141 YaBrowser/22.3.4.731 Yowser/2.5 Safari/537.36'}
response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)

while True:

    with open('page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)

    with open('page.html', 'r', encoding='utf-8') as f:
        html = f.read()

    soup = bs(html, 'html.parser')

    vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:

        vacancy_info = {}
        vacancy_anchor = vacancy.find('a', {'data-qa': "vacancy-serp__vacancy-title"})
        vacancy_name = vacancy_anchor.getText()
        vacancy_info['name'] = vacancy_name

        vacancy_link = vacancy_anchor['href']
        vacancy_info['link'] = vacancy_link

        vacancy_info['site'] = main_url + '/'

        vacancy_salary = vacancy.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"})
        if vacancy_salary is None:
            min_salary = None
            max_salary = None
            currency = None
        else:
            vacancy_salary = vacancy_salary.getText()
            if vacancy_salary.startswith('до'):
                max_salary = int("".join([s for s in vacancy_salary.split() if s.isdigit()]))
                min_salary = None
                currency = vacancy_salary.split()[-1]

            elif vacancy_salary.startswith('от'):
                max_salary = None
                min_salary = int("".join([s for s in vacancy_salary.split() if s.isdigit()]))
                currency = vacancy_salary.split()[-1]

            else:
                max_salary = int("".join([s for s in vacancy_salary.split('–')[1] if s.isdigit()]))
                min_salary = int("".join([s for s in vacancy_salary.split('–')[0] if s.isdigit()]))
                currency = vacancy_salary.split()[-1]

        vacancy_info['max_salary'] = max_salary
        vacancy_info['min_salary'] = min_salary
        vacancy_info['currency'] = currency

        all_vacancies.append(vacancy_info)

    next_button = soup.find('a', {'data-qa': "pager-next"})
    if next_button is None:
        break
    else:
        response = requests.get(main_url + next_button['href'], headers=headers)

print(len(all_vacancies))
# pprint(all_vacancies)

# ДОБАВЛЕНИЕ ТОЛЬКО НОВЫХ ВАКАНСИЙ В ДБ:


def db_update(database, vac_list):

    x = True
    for vac in vac_list:
        for el in database.find({}):
            if el['name'] == vac['name'] and \
               el['max_salary'] == vac['max_salary'] and \
               el['min_salary'] == vac['min_salary'] and \
               el['currency'] == vac['currency']:
                x = False
                break
            else:
                x = True
        if x:
            database.insert_one(vac)
    return database


db_update(vacDB, all_vacancies)
# for i in vacDB.find({}):
#     print(i)

# Подбор вакансий из ДБ по ЗП:


def vacancy_by_salary(database):

    try:
        salary = int(input('Insert desired salary: '))
        s = []
        for el in database.find({'$and': [
            {'$or': [{'min_salary': {'$type': 'number'}}, {'max_salary': {'$type': 'number'}}]},
            {'$or': [{'min_salary': {'$gt': salary}}, {'max_salary': {'$gt': salary}}]}
                                         ]}):
            s.append(el)
        return pprint(s)
    except ValueError:
        print('Salary should be an integer number.')


vacancy_by_salary(vacDB)
