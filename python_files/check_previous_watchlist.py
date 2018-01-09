import bs4

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

# ^ all of the imports for BeautifulSoup

import time
import datetime


def calculations(tick):
    """ Calculate the percent change. """

    url = 'https://finance.yahoo.com/quote/' + tick + '?p=' + tick
    page = get_page(url)

    # gets the current price
    try:
        curr = float(page.findAll('span')[9].text)
    except:
        return

    # gets the previous close price
    try:
        prev_close = float(page.findAll('span', {'class':'Trsdu(0.3s) '})[0].text)
    except:
        return

    # calculates percent change and rounds to 3 decimals
    perc_change = round((((curr / prev_close) - 1) * 100), 2)
    if perc_change >= 5 and perc_change < 15:
        tick_lst.append(tick + '\t' + str(perc_change) + '\tWatch Again')
    elif perc_change >= 15:
        tick_lst.append(tick + '\t' + str(perc_change) + '\tWinner')
    else:
        tick_lst.append(tick + '\t' + str(perc_change))




def get_page(url):
    """ Abstraction to protect against failed URL attempts. """

    sleep_cont = 0
    cont = True

    while cont:
        try:
            client_page = uReq(url)
            cont = False
        except:
            time.sleep(5)
    webpage = client_page.read()

    cont = True
    while cont:
        try:
            client_page = uReq(url)
            webpage = client_page.read()
            cont = False
        except:
            sleep_cont += 1
            time.sleep(7.5)
            if sleep_cont > 5:
                print('Something seems to be wrong with your connection')

    client_page.close()
    return(soup(webpage, 'html.parser'))



today = datetime.datetime.today()

year = str(today.year)[2:]
month = str(today.month)
day = str(today.day)

check_lst = ['Stocks with Positive Price and Volume Trend:', 'Shares with Shorts >= 15%:', 'Shares with price uptrend for 4 or more days:', 'Possible Great Stocks (Short Pain, 4 Day Price Uptrend):', 'The Perfect Stocks (Positive Price, Volume Trend, High Short Shares Float. Does not Check Beta) (Short Pain, 4 Day Price Uptrend):', 'Top 10 Stocks Experiencing Greatest Pain (Short Pain):']

tick_lst = []
prev_watchlist = '../watch_lists/' + str(today.year) + '/' + month + '/watch_lists' + '/watch_list_for_' + month + '_' + day + '_' + year + '.txt'

with open(prev_watchlist, 'r+') as f:
    get = False
    for line in f:
        # determines when to start getting the prices
        if not get:
            if line == '\n':
                prev_line_new += 1
            else:
                prev_line_new = 0
            if prev_line_new == 3:
                get = True

        # if get is True, it will append to the write_list
        else:
            tick = ''
            line = line.strip()

            if line in check_lst:
                tick_lst.append('\n\n' + line + '\n')
            elif line != '\n':
                for char in line:
                    if char == '\t':
                        break
                    tick += char
                calculations(tick)


#print('Prefetching webpages:')



check_watchlist = '../watch_lists/' + str(today.year) + '/' + month + '/checked_watch_lists/' + month + '_' + day + '_' + year + '_checked.txt'

with open(check_watchlist, 'w+') as f:
    for ticker in tick_lst:
        f.write(ticker + '\n')
