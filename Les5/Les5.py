import time
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
# import getpass
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import hashlib

client = MongoClient('127.0.0.1', 27017)
db = client['mailDB']
mailDB = db.mailDB

h = hashlib.new('sha256')

login = 'study.ai_172@mail.ru'  # input('Enter login on mail.ru: ')
password = 'NextPassword172#'  # input('Enter password on mail.ru: ')

s = Service('./chromedriver')
options = Options()
options.add_argument('start-maximized')
driver = webdriver.Chrome(service=s)


driver.get("https://mail.ru/")
driver.implicitly_wait(10)

link = driver.find_element(By.XPATH, "//a[@data-testid='logged-out-email']").get_attribute('href')

driver.get(link)

# time.sleep(5)
input = driver.find_element(By.XPATH, "//input[@name= 'username']")
input.send_keys(login)

button = driver.find_element(By.XPATH, "//button[contains(@data-test-id,'next-button')]")
button.click()
# time.sleep(2)
input = driver.find_element(By.XPATH, "//input[contains(@name,'password')]")
input.send_keys(password)

button = driver.find_element(By.XPATH, "//button[contains(@data-test-id,'submit-button')]")
button.click()
letters_links = set()

while True:
    letters = driver.find_elements(By.XPATH, "//a[contains(@class,'llc')]")
    last = letters[-1]
    for el in letters:
        letters_links.add(el.get_attribute('href'))
    actions = ActionChains(driver)
    actions.move_to_element(last)
    actions.perform()
    time.sleep(2)
    letters = driver.find_elements(By.XPATH, "//a[contains(@class,'llc')]")
    if last == letters[-1]:
        break

mail = []
today = date.today()
yesterday = today - timedelta(1)
for el in letters_links:
    letter_info = {}
    driver.get(el)

    # Извлекаем автора письма
    author = driver.find_element(By.XPATH, "//div[@class='letter__author']/span").text

    # Извлекаем дату отправки письма
    sent_date = driver.find_element(By.CLASS_NAME, "letter__date").text.\
        replace('Сегодня', today.strftime("%d %B")).\
        replace('Вчера', yesterday.strftime("%d %B"))

    # Извлекаем тему письма
    subject = driver.find_element(By.CLASS_NAME, "thread-subject").text

    # Извлекаем текст письма
    text = driver.find_element(By.CLASS_NAME, "letter__body").text

    # Собираем всё в один список
    letter_info['author'] = author
    letter_info['date'] = sent_date
    letter_info['subject'] = subject
    letter_info['text'] = text

    mail.append(letter_info)


def db_update(database, content):

    for n in content:
        try:
            # Генерируем id по теме
            b_name = bytes(n['subject'][0], 'utf-8')
            h.update(b_name)
            _id = h.hexdigest()
            database.insert_one({'_id': _id, **n})
        except DuplicateKeyError:
            print('The letter has already been added to database.')


db_update(mailDB, mail)
