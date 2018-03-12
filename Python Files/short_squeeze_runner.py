# Created By: Ryan M. Elliott, Computer Science student at California Polytechnic State University, San Luis Obispo
# GitHub: https://github.com/RyanElliott10
# Created: December 11, 2017
# Algorithmic program to determine whether a stock is a potential candidate for a short squeeze
# Supporting files: short_squeeze_ds.py


# supporting files
import short_squeeze_ds
import csv

import data_support
import ds

import shutil

# imports for Pandas
import pandas as pd
import pandas_datareader.data as web


def insert_from_csv(csv_lst, hash_table, max_price, stop_num=9999999):
    """ Takes in a list of CSV files that are then inserted. """

    for f in csv_lst:
        with open(f, 'rt') as filename:
            reader = csv.reader(filename, 'excel')
            for i, row in enumerate(reader):
                if i == stop_num:
                    break
                if row[0] != 'Symbol' and '^' not in row[0] and '.' not in row[0] and row[2] != 'n/a' and float(
                        row[2]) <= max_price and len(row[0]) < 5 and row[0] != 'TVIX' and row[0] != 'VIIZ' and 'M' in \
                        row[3]:
                    hash_table.insert(row[0])


def manual_insert(lst, hash_table):
    """ Allows the user to manually enter tickers, mainly for testing. """

    for row in lst:
        hash_table.insert(row)



def runner(mode): # In the future, take in command line args here

    hash_table = short_squeeze_ds.Hash()

    # src1 = "../../../../../Downloads/companylist.csv"
    # src2 = "../../../../../Downloads/companylist-2.csv"
    # src3 = "../../../../../Downloads/companylist-3.csv"
    # dst = "../Support\ Files/CSV\ Files/"

    # shutil.move(src1, dst)
    # shutil.move(src2, dst)
    # shutil.move(src3, dst)

    if mode == 0:
        # test
        csv_lst = ['../Support Files/CSV Files/companylist-2.csv']
    elif mode == 1:
        # full run
        csv_lst = ['../Support Files/CSV Files/companylist.csv', '../Support Files/CSV Files/companylist-2.csv',
               '../Support Files/CSV Files/companylist-3.csv']

    #To-Do: Ask for user input to determine what to do (run full, or test up to n amount of tickers)

    insert_from_csv(csv_lst, hash_table, 7.50)

    print('Total tickers to search:', hash_table.num_items, '\n')

    print('Prefetching webpages:')
    hash_table.pre_fetch_webpages()

    print('\n' + 'Screening stocks:')
    hash_table.init_run()

    print('\n' + 'Checking watchlist:')
    hash_table.check_watchlist()


def main():
    mode = input("Mode (Test/Full): ")
    for char in 'test':
        if char in mode.lower():
            mode = 0
            break
    if mode != 0:
        for char in 'full':
            if char in mode.lower():
                mode = 1
                break
    if mode != 0 and mode != 1:
        mode = 1
    runner(mode)


if __name__ == "__main__":
    main()
