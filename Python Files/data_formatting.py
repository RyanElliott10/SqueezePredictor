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

import os.path


class Security:

    def __init__(self, ticker, page):
        self.ticker = ticker
        self.page = page
        self.lst_of_lsts = [[], [], [], [], [], []]


class Runner:

    def __init__(self):
        self.year = 17
        self.month = (12, False)
        self.day = 29
        self.csv_file = open('sample.csv', 'w')
        self.tickers_already_searched = []
        self.days = []
        self.conn = sqlite3.connect("test_db")
        self.curs = self.conn.cursor()



    def update_date(self):
        """ Updates the date to be used to access watchlist file. """

        # February is only day with 29 days (28 in Leap Year)
        # Formatted as (self.month number, exactly thirty days in self.month)
        months = [(1, False), (2, False), (3, False), (4, True), (5, False), (6, True), (7, False), (8, False),
                  (9, True), (10, False), (11, True), (12, False)]

        # Updates Day
        unchanged = False
        if self.day == 31:
            self.day = 1
        elif self.day == 30 and months[self.month[0] - 1][1]:
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



    # @param: line (from file being read) to be parsed
    def parse_line(self, line):
        """ Parses line in file being read from to gather the tickers. """

        ticker = ''
        for char in line:
            if char != '\t':
                ticker += char
            else:
                return ticker.strip()



    # @param: ticker (Security object)
    def get_data(self, ticker):
        """ Gets the data for the all the stocks. """

        # tr_lst = ticker.page.findAll('tr', {'class': 'BdT Bdc($c-fuji-grey-c) Ta(end) Fz(s) Whs(nw)'})

        ticker.page = ticker.page.text

        keyword_lst = [ticker.page.index("timestamp"), ticker.page.index("open"), ticker.page.index("high"), ticker.page.index("low"), ticker.page.index("adjclose"), ticker.page.index("volume")]


        for i in range(len(keyword_lst)):
            self.parse_data_column(keyword_lst[i], i, ticker)

        # if ticker.ticker == 'HTBX':
            # print(ticker.lst_of_lsts)

        self.write_to_file(ticker)



    # @param: page_index (index of current thing to be searched (open, high, low, etc.))
    # @param: index to be used to access correct list in lst_of_lsts
    # @param: Ticker (Security object)
    def parse_data_column(self, page_index, index, ticker):
        """ Parses the page at a given index (open, close, etc.) and adds to ticker.lst_of_lsts. """

        lst = []
        num = ''
        for char in ticker.page[page_index:]:
            if char == ']':
                break
            if char != '"' and char != ':' and char != '[' and char != ',':
                num += char
            else:
                try:
                    # parses date as YYYY-MM-DD
                    if index == 0:
                        lst.append(time.strftime('%Y-%m-%d', time.localtime(float(num))))
                    else:
                        lst.append(round(float(num), 5))
                except:
                    pass
                num = ''

        ticker.lst_of_lsts[index] = lst



    def write_to_file(self, ticker):
        """ Writes to the CSV file (not currently in use) and database. """

        writer = csv.writer(self.csv_file, dialect='excel')
        writer.writerow([ticker.ticker])
        for thing in ticker.lst_of_lsts:
            thing.reverse()
            # writer.writerow(thing)
        self.store_in_db(ticker)



    def open_watchlist(self):
        today = datetime.datetime.today()
        unique_tickers = []
        count = 0

        self.curs.execute(
            "CREATE TABLE IF NOT EXISTS data(ticker TEXT, date TEXT, open REAL, high REAL, low REAL, close REAL, volume INTEGER)")

        # while self.year <= int(str(today.year)[2:]) and self.month[0] <= today.month and self.day <= today.day:
        while count < 100:
            watchlist = '../Watchlists/20' + str(self.year) + '/' + str(self.month[0]) + '/Watchlists' + '/watch_list_for_' + str(self.month[0]) + '_' + str(
                self.day) + '_' + str(self.year) + '.txt'

            if os.path.exists(watchlist):
                self.days.append(str(str(self.month[0]) + '/' + str(self.day) + '/' + str(self.year)))
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
        print('\nWriting to CSV file and database')

        for tick in self.tickers_already_searched:
            if type(tick) is not str:
                self.get_data(tick)

        self.csv_file.close()
        self.curs.close()
        self.conn.close()



    def pre_fetch_webpages(self):
        requests_cache.install_cache('cache', backend='sqlite', expire_after=3600)
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            bar = progressbar.ProgressBar(max_value=len(self.tickers_already_searched) - 1)
            future_to_tickers = {executor.submit(self.get_page_async, nd): nd for nd in self.tickers_already_searched}
            foo = 0
            for future in concurrent.futures.as_completed(future_to_tickers):
                if foo >= len(self.tickers_already_searched) - 1:
                    foo = foo - 1
                bar.update(foo + 1)
                foo += 1



    def get_page_async(self, nd):
        if nd is not None:
            url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + nd + '?formatted=true&crumb=h.8f9xpa6IF&lang=en-US&region=US&interval=1d&events=div%7Csplit&range=1y&corsDomain=finance.yahoo.com'
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
                    print(url)
                    break

        return (soup(webpage, 'html.parser'))



    def store_in_db(self, ticker):
        """ Write the data from each stock into the database. """

        # allows access to global variable, curs
        db_lsts = []

        # print(len(ticker.lst_of_lsts[0]))
        l1_len = len(ticker.lst_of_lsts[0])

        lsts = ticker.lst_of_lsts

        if l1_len != len(lsts[1]) and l1_len != len(lsts[2]) and l1_len != len(lsts[3]) and l1_len != len(lsts[4]) and l1_len != len(lsts[5]):
            return
        for date in range(len(lsts[0])):
            inner_lst = []
            for type in range(6):
                inner_lst.append(lsts[type][date])
            db_lsts.append(inner_lst)

        for thing in db_lsts:
            self.curs.execute("INSERT INTO data VALUES(?, ?, ?, ?, ?, ?, ?)",
                              (ticker.ticker, thing[0], thing[1], thing[2], thing[3], thing[4], thing[5]))
            self.conn.commit()



def main():
    # initializing the db, connecting, and ensuring the table (data) is already there

    rn = Runner()
    rn.open_watchlist()


if __name__ == "__main__":
    main()

# TODO: Write into a file the last day I left off on, then implement a way for the program to essentailly pick up from that point.
# TODO: Find out how to run it several times and not have it duplicate values

# BUG: The while condition does not work. Right now, a counter will do the trick, but you gots to fix this.
