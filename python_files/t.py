import csv

# imports for BeautifulSoup
from bs4 import BeautifulSoup as soup

import time
import datetime

# imports for progressbar, website prefetching
import requests
import progressbar
import requests_cache
import concurrent.futures

import sqlite3

url = 'https://query1.finance.yahoo.com/v8/finance/chart/QQQ?formatted=true&crumb=h.8f9xpa6IF&lang=en-US&region=US&interval=1d&events=div%7Csplit&range=1y&corsDomain=finance.yahoo.com'

def parse(index):
    lst = []
    num = ''
    for char in page[index:]:
        if char == ']':
            break
        if char != '"' and char != ':' and char != '[' and char != ',':
            num += char
        else:
            try:
                lst.append(float(num))
            except:
                pass
            num = ''
    return lst


webpage = requests.get(url).text
cont = False

page = soup(webpage, 'html.parser').text


keyword_lst = [page.index("timestamp"), page.index("open"), page.index("high"), page.index("low"), page.index("adjclose"), page.index("volume")]


for i in range(len(keyword_lst)):
    print(parse(keyword_lst[i]), '\n\n\n\n')


# https://query1.finance.yahoo.com/v8/finance/chart/AAPL?formatted=true&crumb=h.8f9xpa6IF&lang=en-US&region=US&interval=1d&events=div%7Csplit&range=1y&corsDomain=finance.yahoo.com

# https://query1.finance.yahoo.com/v8/finance/chart/DRYS?formatted=true&crumb=h.8f9xpa6IF&lang=en-US&region=US&interval=1d&events=div%7Csplit&range=1y&corsDomain=finance.yahoo.com