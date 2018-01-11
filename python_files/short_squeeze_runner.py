# Created By: Ryan M. Elliott, Computer Science student at California Polytechnic State University, San Luis Obispo
# GitHub: https://github.com/RyanElliott10
# Created: December 11, 2017
# Algorithmic program to determine whether a stock is a potential candidate for a short squeeze
# Supporting files: short_squeeze_ds.py


# supporting files
import short_squeeze_ds
import csv

# imports for Yahoo! Finance API, Pandas, and MatPlotLib
import datetime
"""import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates"""
import pandas as pd
import pandas_datareader.data as web
from yahoo_finance import Share


def insert_from_csv(csv_lst, stop_num=999999):
    """ Takes in a list of CSV files that are then inserted. """

    for f in csv_lst:
        with open(f, 'rt') as filename:
            reader = csv.reader(filename, 'excel')
            for i, row in enumerate(reader):
                if i == stop_num:
                    break
                if row[0] != 'Symbol' and '^' not in row[0] and '.' not in row[0] and row[2] != 'n/a' and float(row[2]) <= 10 and len(row[0]) < 5 and row[0] != 'TVIX' and row[0] != 'VIIZ' and 'M' in row[3]:
                        hash_table.insert(row[0])


def manual_insert(lst):
    """ Allows the user to manually enter tickers, mainly for testing. """

    for row in lst:
        hash_table.insert(row)




hash_table = short_squeeze_ds.Hash()


csv_lst = ['../support_files/csv_files/companylist.csv', '../support_files/csv_files/companylist-2.csv', '../support_files/csv_files/companylist-3.csv']
csv_lst2 = ['../support_files/csv_files/companylist-2.csv']
manual_tickers = []

insert_from_csv(csv_lst)
#manual_insert('MIN')

print('Total tickers to search:', hash_table.num_items, '\n')
#TODO: allow user to skip pre-fetch .. this will also invalidate cache
print('Prefetching webpages:')
hash_table.pre_fetch_webpages()
print('\n' + 'Screening stocks:')
hash_table.init_run()
print('\n' + 'Checking watchlist:')
hash_table.check_watchlist()
