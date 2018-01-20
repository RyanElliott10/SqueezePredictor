# imports for BeautifulSoup
import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

import time
import datetime

# imports for progressbar, website prefetching
import requests
import progressbar
import requests_cache
import concurrent.futures




def calculations(tick, calc_count):
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

    # calculates percent change and rounds to 2 decimals
    perc_change = round((((curr / prev_close) - 1) * 100), 2)


    changed = False
    for key in check_dict:
        if check_dict[key] == calc_count:
            tick_lst.append('\n\n' + key + '\n')
            changed = True
            out_key = key
    if changed:
        del check_dict[out_key]

    if perc_change >= 5 and perc_change < 15:
        tick_lst.append(tick + '\t' + str(perc_change) + '\tWatch Again')
    elif perc_change >= 15:
        tick_lst.append(tick + '\t' + str(perc_change) + '\tWinner')
    else:
        tick_lst.append(tick + '\t' + str(perc_change))

    return(changed)



def get_page(url):
    """ Abstraction to protect against failed URL attempts. """

    sleep_cont = 0
    cont = True

    while cont:
        try:
            webpage = requests.get(url).text
            cont = False
        except:
            sleep_cont += 1
            time.sleep(5)
            if sleep_cont > 5:
                print('Something seems to be wrong with your connection')

    return(soup(webpage, 'html.parser'))







today = datetime.datetime.today()

year = str(today.year)[2:]
month = str(today.month)
day = str(today.day)

check_lst = ['Stocks with Positive Price and Volume Trend:', 'Shares with Shorts >= 15%:', 'Shares with price uptrend for 4 or more days and near 52 week low:', 'Possible Great Stocks (4 Day Price Uptrend):', 'The Perfect Stocks (Positive Price, Volume Trend, High Short Shares Float. Does not Check Beta) (Short Pain, 4 Day Price Uptrend):', 'Top 10 Stocks Experiencing Greatest Pain (Short Pain):', 'Shares within 35% of 52 week low:']

tick_lst = ['Stocks with Positive Price and Volume Trend:\n']
tickers = []
check_dict = {}
prev_watchlist = '../watch_lists/' + str(today.year) + '/' + month + '/watch_lists' + '/watch_list_for_' + month + '_' + day + '_' + year + '.txt'




with open(prev_watchlist, 'r+') as f:
    get = False
    count = 0

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
            count += 1
            tick = ''
            line = line.strip()

            if line == 'Stocks with Positive Price and Volume Trend:':
                check_dict[line] = count
                first_count = count
                #count = 0
            elif line in check_lst:
                check_dict[line] = count
                #count = 0
            elif line != '\n':
                for char in line:
                    if char == '\t':
                        break
                    tick += char
                tickers.append(tick)





#Utility function to prefetch webpages concurrently
def pre_fetch_webpages():
    requests_cache.install_cache('cache', backend='sqlite', expire_after=3600)
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        #bar = progressbar.ProgressBar(max_value=len(tickers)-1)
        future_to_tickers = {executor.submit(get_page_async, nd): nd for nd in tickers}
        #foo = 0
        #for future in concurrent.futures.as_completed(future_to_tickers):
            #bar.update(foo)
            #oo += 1


def get_page_async(nd):
    if nd is not None:
        ticker = nd.ticker
        url = 'https://finance.yahoo.com/quote/' + tick + '?p=' + tick
        page = get_page(url)





calc_count = 1
#print('Prefetching webpages:')
pre_fetch_webpages()
#print('\n' + 'Checking previous watchlist:')
for nd in tickers:
    calc_count += 1
    if(calculations(nd, calc_count)):
        calc_count += 1




check_watchlist = '../watch_lists/' + str(today.year) + '/' + month + '/checked_watch_lists/' + month + '_' + day + '_' + year + '_checked.txt'

with open(check_watchlist, 'w+') as f:
    for ticker in tick_lst:
        f.write(ticker + '\n')
