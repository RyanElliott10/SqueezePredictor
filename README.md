# Short Squeeze Predictor

## Disclaimer
This project was initiated by a younger, more naive self. Rather than using Python's built in dict (and therefore hashing), I wrote my own (poorly implemented) hashtable as practice. I regret nothing, but proceed with using this code at your own risk.

## About

A Python script to gather a list of tickers from a CSV file, scrape data from Yahoo! Finance, analyze historical and current data for each security, and determine its susceptibility to a short squeeze. Upcoming feature: machine learning implementation to use previous data and determine which data is needed to determine a stock's viablity to be squeezed.

Running runner.py will run a script which will parse a CSV file (included if git clone), collect tickers, prefetch the appropriate Yahoo! Finance pages to gather data, then scrape that data and write the stocks most susceptible to a short squeeze into a .txt file (watch_list_for_next_day_date.txt).

Running check_previous_watchlist.py will run a script which will parse the previous day's wathclist and again scrape data from Yahoo! Finance and determine whether it was a winner (+15%) or not.

Running data_formatting.py will run a script which parses all of the previous watchlist .txt files, collects every unique ticker, gathers historical data up to a year old, and stores it into a SQLite database.

Works on Python 2.7+ and 3.5+

## Python Library Installs

pip install requests

pip install beautifulsoup

pip install progressbar

pip install requests_cache

pip install request

pip install pandas


## Tools

SQLite

## Run

python runner.py

python check_previous_watchlist.py

python data_formatting.py
