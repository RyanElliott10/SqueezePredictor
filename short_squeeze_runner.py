# Created By: Ryan M. Elliott, Computer Science student at California Polytechnic State University, SLO
# GitHub:
# Created: December 11, 2017
# Algorithmic program to determine whether a stock is a potential candidate for a short squeeze
# Supporting classes: short_squeeze_ds.py, ss_ds_node.py


import short_squeeze_ds
import csv

import datetime
"""import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates"""
import pandas as pd
import pandas_datareader.data as web
from yahoo_finance import Share

# ^ all of the imports to use Yahoo! Finance API, Pandas, and MatPlotLib




# YOU REALLY SHOULD WRITE A METHOD TO ALLOW YOU TO MANUALLY ENTER TICKERS INTO THE WATCHLIST


hash_table = short_squeeze_ds.Hash()

csv_lst = ['/CSV_files/companylist.csv', '/CSV_files/companylist (1).csv', 'CSV_files/companylist (2).csv']
#csv_lst = ['companylist (1).csv']


for f in csv_lst:
    with open(f, 'rt') as filename:
        reader = csv.reader(filename, 'excel')
        for row in reader:
            if row[0] != 'Symbol' and '^' not in row[0] and '.' not in row[0] and row[2] != 'n/a' and float(row[2]) <= 10 and len(row[0]) < 5 and row[0] != 'TVIX' and row[0] != 'VIIZ' and 'M' in row[3]:
                    hash_table.insert(row[0])

#hash_table.insert('AMD')

print('Total tickers to search:', hash_table.num_items, '\n')
hash_table.init_run()
hash_table.check_watchlist()
