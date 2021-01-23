import requests
from bs4 import BeautifulSoup

response = requests.get('http://www.finmarket.ru/currency/rates/')
page = response.text
soup = BeautifulSoup(page, 'html.parser')
currency = []
for figures in soup.select('div.value'):
    currency.append(figures.text)
rub_usd = float(currency[0].replace(',', '.'))
rub_eur = float(currency[1].replace(',', '.'))
