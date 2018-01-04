import bs4

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

# ^ all of the imports for BeautifulSoup

import time
import datetime



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

check_lst = ['Stocks with Positive Price and Volume Trend:', 'Stocks with High Beta:', 'Possible Good Stocks (Short Pain, Within 15% of 52 Week Low):', 'Possible Great Stocks (Short Pain, Within 15% of 52 Week Low):', 'Shares with Shorts >= 15%:', 'The Perfect Stocks (Positive Price, Volume Trend, High Short Shares Float. Does not Check Beta) (Short Pain, Within 15% of 52 Week Low):', 'Top 10 Stocks Experiencing Greatest Pain (Short Pain, Within 15% of 52 Week Low):']

tick_lst = []

prev_watchlist = './watch_lists/' + str(today.year) + '/' + month + '/checked_watch_lists' + '/watch_list_for_' + month + '_' + day + '_' + year + '.txt'
#prev_watchlist = './watch_lists/watch_list_for_' + month + '_' + day + '_' + year + '.txt'

with open(prev_watchlist, 'r+') as f:
    get = False
    for line in f:
        tick = ''
        cont = True
        line = line.strip()
        for char in line:
            if char == ' ':
                cont = False
            elif cont:
                tick = tick + char
        if get and len(line) <= 15 and len(line) >= 1:
            url = 'https://finance.yahoo.com/quote/' + tick + '?p=' + tick
            page = get_page(url)

            # gets the current price
            curr = float(page.findAll('span')[9].text)

            # gets the previous close price
            prev_close = float(page.findAll('span', {'class':'Trsdu(0.3s) '})[0].text)

            # calculates percent change and rounds to 3 decimals
            perc_change = round((((curr / prev_close) - 1) * 100), 3)
            if perc_change >= 5 and perc_change < 15:
                tick_lst.append(tick + '\t' + str(perc_change) + '\tWatch Again')
            elif perc_change >= 15:
                tick_lst.append(tick + '\t' + str(perc_change) + '\tWinner')
            else:
                tick_lst.append(tick + '\t' + str(perc_change))
        elif line == 'High Shorts Float:':
            tick_lst.append(line + '\n')
            get = True
        elif line in check_lst:
            tick_lst.append('\n\n' + line + '\n')
            get = True



check_watchlist = './watch_lists/watch_list_for_' + year + '/' + month + 'checked_watch_lists/' + '_' + day + '_' + year + '_checked.txt'

with open(check_watchlist, 'w+') as f:
    for ticker in tick_lst:
        f.write(ticker + '\n')
