# imports for BeautifulSoup
import operator
import bs4
from bs4 import BeautifulSoup as soup

# imports for progressbar, website prefetching
import requests
import progressbar
import requests_cache
import concurrent.futures


# nodes used in the hash table
class Node:

	def __init__(self, ticker):
		self.next = None
		self.prev = None
		self.ticker = ticker
		self.prev_close = 0
		self.curr_price = 0
		self.perc_change = 0
		self.avg_volume = 0
		self.vol_uptrend = True
		self.price_uptrend = True
		self.high_shorts = True
		self.high_beta = True
		self.days_twenty_perc_above_avg_volume = 0
		self.shorts_percent_float = 0
		self.shorts_pain = 0
		self.days_to_cover = 0
		self.main_page = None
		self.history_page = None
		self.key_statistics_page = None


class Hash:
	""" Creates a hash table utilizing quadratic probing. """

	def __init__(self, size=7949):

		self.capacity = size
		self.num_items = 0
		self.hash_table = [None] * self.capacity
		self.primes_list = []
		self.watchlist = []
		self.neg_vol_trend_list = []
		self.pos_vol_trend_list = []
		self.neg_price_trend_list = []
		self.pos_price_trend_list = []
		self.removed_list = []
		self.low_short_shares = []
		self.high_short_shares = []
		self.high_beta_lst = []
		self.low_beta_lst = []
		self.high_shares_perc_change = []
		self.write_list = []
		self.good_yearly_low = []
		self.bad_yearly_low = []
		self.four_day_uptrend = []
		self.ranked_shares = {}
		self.sorted_ranked_shares = None
		self.get_primes('../Support Files/primes_to_200000.txt')


	def get_primes(self, filename):
		""" Reads from file containing list of primes up to 200000 and appends each prime to a list. """

		f = open(filename)
		for word in f.read().split():
			self.primes_list.append(int(word))


	def get_load_fact(self):
		return self.num_items / len(self.hash_table)


	def my_hash(self, key, num):
		return (key + (num * num)) % len(self.hash_table)


	def find_capacity(self):
		for val in self.primes_list:
			if self.capacity * 2 < val:
				self.capacity = val
				break


	def rehash(self):
		""" Rehashes the entire hash_table. """
		# Figure out a way to set a new table to one efficiently, don't just do self.hash_table = tmp_table

		self.find_capacity()
		tmp_table = [None] * self.capacity

		for val in self.hash_table:
			if val:  # if there is a value in the slot, rehash into new slot
				key = 1
				ticker = val.ticker

				for char in ticker:
					key *= ord(char)

				num = 2
				cont = True

				while cont:
					hash_val = self.my_hash(key, num)

					if tmp_table[hash_val] is None:
						self.num_items += 1
						tmp_table[hash_val] = val
						cont = False
					num += 1

		self.hash_table = tmp_table


	def insert(self, ticker):
		""" The key will be the ascii value of each char multiplied by the total so far. Returns -1 if it cannot be entered. """

		nd = Node(ticker)
		key = 1

		for char in ticker:
			key *= ord(char)

		val = 2
		cont = True
		collisions = -1

		while cont:
			hash_val = self.my_hash(key, val)
			collisions += 1
			if collisions >= self.capacity:
				self.rehash()
				collisions = -1

			if self.hash_table[hash_val] is not None and self.hash_table[hash_val].ticker == ticker:
				cont = False
			elif self.hash_table[hash_val] is None:
				self.num_items += 1
				if self.get_load_fact() >= 0.5:
					self.rehash()
				if self.hash_table[hash_val] is None:
					self.hash_table[hash_val] = nd
					cont = False
					return hash_val
			val += 1
		return -1


	def remove(self, ticker):
		""" Will remove the node at the hash_value. Returns -1 if not found. """

		key = 1

		for char in ticker:
			key *= ord(char)

		val = 2
		while val < self.capacity:
			hash_val = self.my_hash(key, val)

			if self.hash_table[hash_val] and self.hash_table[hash_val].ticker == ticker:
				tmp = self.hash_table[hash_val]
				self.hash_table[hash_val] = None
				return tmp
			val += 1
		return -1


	def get(self, ticker):
		""" Will return the node which will allow you to access whatever you want (ticker, price, etc.). """

		key = 1
		ticker = ticker.upper()

		for char in ticker:
			key *= ord(char)

		val = 2
		while val < self.capacity:
			hash_val = self.my_hash(key, val)

			if self.hash_table[hash_val] and self.hash_table[hash_val].ticker == ticker:
				return self.hash_table[hash_val]
			val += 1

		return -1


	def print_ticker(self):
		for val in self.hash_table:
			if val is not None:
				print('$' + val.ticker)


	# Utility function to prefetch webpages concurrently
	def prefetch_webpages(self):
		requests_cache.install_cache('cache', backend='sqlite', expire_after=3600)
		with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
			bar = progressbar.ProgressBar(max_value=self.num_items)
			future_to_tickers = {executor.submit(self.get_page, nd): nd for nd in self.hash_table if nd is not None}
			foo = 0
			for future in concurrent.futures.as_completed(future_to_tickers):
				if foo >= len(self.hash_table):
					foo = foo - 1
				bar.update(foo + 1)
				foo += 1
			bar.update(self.num_items)


	def get_page(self, nd):
		""" Abstraction to protect against failed URL attempts. """

		ticker = nd.ticker

		url1 = ('https://finance.yahoo.com/quote/{0}?p={0}'.format(ticker)).strip()
		url2 = ('https://finance.yahoo.com/quote/{0}/history?p={0}'.format(ticker)).strip()
		url3 = ('https://finance.yahoo.com/quote/{0}/key-statistics?p={0}'.format(ticker)).strip()

		sess = requests.session()

		nd.main_page = soup(sess.get(url1, headers={'User-Agent': 'Custom'}).text, 'html.parser')
		nd.history_page = soup(sess.get(url2, headers={'User-Agent': 'Custom'}).text, 'html.parser')
		nd.key_statistics_page = soup(sess.get(url3, headers={'User-Agent': 'Custom'}).text, 'html.parser')
