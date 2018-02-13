# Import all the important libraries to parse the HTML page

import csv
import requests

import matplotlib.pyplot as plt
from matplotlib import style

#from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
import pandas_datareader.data as web
from yahoo_finance import Share

#from datetime import date
import datetime
import time

import sys

import bs4

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
# ^ all of the imports for BeautifulSoup



string = 'XIV'
string.strip()

tick = ''
for char in string:
    if char == '\t':
        break
    tick += char

"""for char in string:
    print(repr(char))"""


url = 'https://finance.yahoo.com/quote/LEJU?p=LEJU'

# while cont:
#     try:
#         client_page = uReq(url)
#         webpage = client_page.read()
#         cont = False
#     except:
#         sleep_cont += 1
#         time.sleep(5)
#         if sleep_cont > 5:
#             self.write_list.append('Something seems to be wrong with your connection\n')

curr = ""

while type(curr) is not bs4.BeautifulSoup:
    print(type(curr))
    client_page = uReq(url)
    webpage = client_page.read()

    client_page.close()
    page = soup(webpage, 'html.parser')

    # curr = page.encode(sys.stdout.encoding).decode('utf-8')#, errors='backslashreplace').decode('utf-8')
    # curr = page.encode(sys.stdout.encoding, errors='backslashreplace').decode('utf-8')
    curr = page.decode('utf-8')
    curr = soup(curr, 'html.parser')

print(curr)


# start = datetime.datetime(2017, 12, 10)
# cont = True
# while cont:
#     try:
#         df = web.DataReader('CCHI', 'yahoo', start)
#         cont = False
#     except:
#         pass
# print(df)







today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

# [month, day]
closed_dates = [(1, 1), (1, 15), (2, 19), (3, 30), (5, 28), (7, 4), (9, 3), (11, 22), (12, 25)]

time_delta = 1

# tomorrow.weekday() returns int from 0-6, where 0 is Monday and 6 is Sunday
if tomorrow.weekday() == 5:
    time_delta += 2

tomorrow = today + datetime.timedelta(days=time_delta)
month = tomorrow.month
day = tomorrow.day

for date in closed_dates:
    if month == date[0] and day == date[1]:
        time_delta += 1

tomorrow = today + datetime.timedelta(days=time_delta)

year = str(tomorrow.year)[2:]
month = str(tomorrow.month)
day = str(tomorrow.day)
