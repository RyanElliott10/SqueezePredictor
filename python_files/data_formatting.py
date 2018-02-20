import csv

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

import os.path


class Security:

    def __init__(self, ticker, page):
        self.ticker = ticker
        self.page = page
        self.date = []
        self.open = []
        self.high = []
        self.low = []
        self.adj_close = []
        self.volume = []
        self.lst_of_lsts = [self.date, self.open, self.high, self.low, self.adj_close, self.volume]



class Runner:

    def __init__(self):
        self.year = 17
        self.month = (12, False)
        self.day = 29
        self.csv_file = open('sample.csv', 'w')
        self.tickers_already_searched = []
        self.days = []




    def update_date(self):

        # February is only day with 29 days (28 in Leap Year)
        # Formatted as (self.month number, exactly thirty days in self.month)
        months = [(1, False), (2, False), (3, False), (4, True), (5, False), (6, True), (7, False), (8, False), (9, True), (10, False), (11, True), (12, False)]

        # Updates Day
        unchanged = False
        if self.day == 31:
            self.day = 1
        elif self.day == 30 and months[self.month[0]-1][1]:
            self.day = 1
        elif self.day == 29 and self.month[0] == 2:
            self.day = 1
        else:
            unchanged = True
            self.day += 1

        # Updates Month and Year
        if not unchanged:
            if self.month[0] != 12:
                self.month = months[self.month[0]]
            else:
                self.month = months[0]
                self.year += 1
        # print(self.day, self.month[0], self.year)




    def parse_line(self, line):
        ticker = ''
        for char in line:
            if char != '\t':
                ticker += char
            else:
                return ticker.strip()




    def get_data(self, ticker):
        # This will only go back 100 trading days!
        tr_lst = ticker.page.findAll('tr', {'class':'BdT Bdc($c-fuji-grey-c) Ta(end) Fz(s) Whs(nw)'})

        # This starts at index 1 because you don't want to run it during the trading day with values changing
        for index in range(1, len(tr_lst)):
            self.parse_tr(tr_lst[index].findAll('span'), ticker)
        self.write_to_file(ticker)




    def parse_tr(self, string, ticker):
        if len(string) > 3:
            for index, thing in enumerate(string[:4]):
                ticker.lst_of_lsts[index].append(thing.text)
            for index, thing in enumerate(string[5:]):
                ticker.lst_of_lsts[index+4].append(thing.text)




    def write_to_file(self, ticker):
        writer = csv.writer(self.csv_file, dialect='excel')
        # writer.writerow([ticker.ticker, str(str(self.month[0]) + "/" + str(self.day) + "/" + str(self.year))])
        for thing in ticker.lst_of_lsts:
            thing.reverse()
            writer.writerow(thing)




    # Idea: get each ticker from the file, and then add each to a list. Call pre_fetch_webpages, and then creates a Security object with the ticker and webpage. Obviously, create a list of these objects
    def open_watchlist(self):
        today = datetime.datetime.today()
        unique_tickers = []
        count = 0

        # while self.year != int(str(today.year)[:2]) and self.month[0] != today.month and self.day != today.day:
        while count < 100:
            watchlist = '../watch_lists/20' + str(self.year) + '/' + str(self.month[0]) + '/watch_lists' + '/watch_list_for_' + str(self.month[0]) + '_' + str(self.day) + '_' + str(self.year) + '.txt'

            if os.path.exists(watchlist):
                self.days.append(str(str(self.day) + '/' + str(self.month[0]) + '/' + str(self.year)))
                with open(watchlist, 'r') as wfile:
                    for line in wfile:
                        t = self.parse_line(line.strip())
                        if t is not None and len(t.strip()) > 4:
                            t = t.strip()[:4]
                        if 'Tickers that were not found' in line or 'Stocks with Positive Price and Volume Trend:' in line or 'found:' in line:
                            break
                        elif 'Ticker' in line:
                            continue
                        elif t is not None and t not in self.tickers_already_searched and 'Shares' not in line and 'Possible' not in line:
                            self.tickers_already_searched.append(t)
            self.update_date()
            count += 1

        print('Watch Lists Used:', self.days)
        print('\nPrefetching Webpages')
        self.pre_fetch_webpages()
        print('\nWriting to CSV file')
        for tick in self.tickers_already_searched:
            self.get_data(tick)
        self.csv_file.close()




    def pre_fetch_webpages(self):
        requests_cache.install_cache('cache', backend='sqlite', expire_after=3600)
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            bar = progressbar.ProgressBar(max_value=len(self.tickers_already_searched)-1)
            future_to_tickers = {executor.submit(self.get_page_async, nd): nd for nd in self.tickers_already_searched}
            foo = 0
            for future in concurrent.futures.as_completed(future_to_tickers):
                if foo >= len(self.tickers_already_searched)-1:
                    foo = foo-1
                bar.update(foo+1)
                foo += 1




    def get_page_async(self, nd):
        if nd is not None:
            url = 'https://finance.yahoo.com/quote/' + nd + '/history?p=' + nd
            page = self.get_page(url)

            # Goes through the list, replaces the entry at the index of the ticker with a tupe containing (ticker, BS4 soup object)
            for index, tick in enumerate(self.tickers_already_searched):
                if nd == tick:
                    self.tickers_already_searched[index] = Security(tick, page)




    def get_page(self, url):
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
                    break

        return(soup(webpage, 'html.parser'))




def main():
    rn = Runner()
    rn.open_watchlist()

if __name__ == "__main__":
    main()



# TODO: Write into a file the last day I left off on, then implement a way for the program to essentailly pick up from that point.
# TODO: Add in headers that are printed to the csv file that say the day.

# BUG: The while condition does not work. Right now, a counter will do the trick, but you gots to fix this.
