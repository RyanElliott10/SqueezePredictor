# Import all the important libraries to parse the HTML page

import csv
import requests

# from datetime import date
import datetime
import time

import sys

import bs4
from bs4 import BeautifulSoup as soup

import requests
import progressbar
import requests_cache
import concurrent.futures




# url = 'https://finance.yahoo.com/quote/LEJU?p=LEJU'
t_lst = ['AAPL', 'AMD', 'SQ', 'V', 'LEJU', 'BPMX', 'WM', 'MSFT', 'GOOG', 'AMZN']

hash_table = []
for thing in range(200):
    for ticker in t_lst:
        hash_table.append(ticker)



def pre_fetch_webpages():
        requests_cache.install_cache('cache', backend='sqlite', expire_after=3600)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            bar = progressbar.ProgressBar(max_value=len(hash_table))
            future_to_tickers = {executor.submit(get_page_async, nd): nd for nd in hash_table if nd is not None}
            foo = 0
            for future in concurrent.futures.as_completed(future_to_tickers):
                if foo >= len(hash_table) - 1:
                    foo -= 1
                bar.update(foo + 1)
                foo += 1

        bar = progressbar.ProgressBar(max_value=len(hash_table))
        foo = 0
        for thing in hash_table:
            if thing is not None:
                get_page_async(thing)
                print(thing.ticker)



def get_page_async(nd):
    if nd is not None:
        ticker = nd
        get_page(nd)


def get_page(nd):
    """ Abstraction to protect against failed URL attempts. """


    url1 = ('https://finance.yahoo.com/quote/{0}?p={0}'.format(ticker)).strip()
    url2 = ('https://finance.yahoo.com/quote/{0}/history?p={0}'.format(ticker)).strip()
    url3 = ('https://finance.yahoo.com/quote/{0}/key-statistics?p={0}'.format(ticker)).strip()

    sess = requests.session()

    quote = soup(sess.get(url1, headers={'User-Agent': 'Custom'}).text, 'html.parser')
    history = soup(sess.get(url2, headers={'User-Agent': 'Custom'}).text, 'html.parser')
    stats = soup(sess.get(url3, headers={'User-Agent': 'Custom'}).text, 'html.parser')

    print('{0}\n{1}\n{2}', quote, history, stats)


pre_fetch_webpages()
