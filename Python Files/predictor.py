import datetime

# imports for BeautifulSoup
import operator
import bs4
from bs4 import BeautifulSoup as soup

# imports for progressbar, website prefetching
import requests
import progressbar
import requests_cache
import concurrent.futures

class Predictor:
	# Currently, the 'perfect' stock has a volume and price uptrend, >= 5% shares float, beta > 1% or < -1, price at or below $10.00,
	# and daily percent change between the days is >= 5%.

	def init_run(self, hash_table):
		""" Screens the stocks and adds to watchlist if their daily percent change is >= 5. """

		not_lst = []

		hash_table.write_list.append('Ticker\t% Chng\n\n')

		bar = progressbar.ProgressBar(max_value=hash_table.num_items - 1)
		foo = 0
		for nd in hash_table.hash_table:
			if nd is not None:
				bar.update(foo)
				foo += 1
				cont = True
				ticker = nd.ticker

				# safeguards against a failed URL attempt
				page = nd.main_page

				# gets the current price
				try:
					nd.curr_price = float(page.findAll('span')[10].text.strip())
				except:
					not_lst.append(ticker)
					cont = False

				if cont:
					# checks if the stock is within 35% of 52 week low
					self.check_yearly_low(nd, page, hash_table)

					# gets the previous close price and average volume
					for thing in page.findAll('tr'):
						if 'Previous Close' in thing.text:
							nd.prev_close = float(thing.text.strip()[14:])
						elif 'Avg. Volume' in thing.text:
							try:
								nd.avg_volume = float(thing.text.strip()[13:].replace(',', ''))
							except:
								not_lst.append(ticker)
								return
							break
					if not nd.prev_close or not nd.avg_volume:
						not_lst.append(ticker)

					# calculates percent change and rounds to 3 decimals
					try:
						nd.perc_change = round((((nd.curr_price / nd.prev_close) - 1) * 100), 3)
					except:
						nd.perc_change = 0

					# appends to the watchlist if it fits criteria
					if nd.perc_change >= 5 or (nd.perc_change > 0 and self.alt_price_uptrend(nd)):
						hash_table.write_list.append(str(ticker + '\t' + str(nd.perc_change) + '\n'))
						hash_table.watchlist.append(nd)

		# prints the tickers not found, if any
		if len(not_lst) != 0:
			word = ''
			for i, val in enumerate(not_lst):
				if i != 0:
					word = word + ', ' + val
				else:
					word = val
			hash_table.write_list.append(str('\nTickers that were not found: ' + word + '\n'))



	def check_watchlist(self, hash_table):
		""" Further screens the watchlist. Calls functions that call other functions. """

		if len(hash_table.watchlist) > 0:
			bar = progressbar.ProgressBar(max_value=len(hash_table.watchlist) - 1)
		else:
			bar = progressbar.ProgressBar(max_value=0)
		foo = 0

		for nd in hash_table.watchlist:
			bar.update(foo)
			foo += 1
			ticker = nd.ticker

			page = nd.history_page

			self.check_volume_trend(nd, page, hash_table)
			self.check_price_trend(nd, page, hash_table)
			self.check_shorts_beta(nd, hash_table)
			self.check_pain(nd, hash_table)

		append_dict = {}
		hash_table.write_list.append('\n\n\nStocks with Positive Price and Volume Trend:\n')
		for nd in hash_table.pos_vol_trend_list:
			hash_table.write_list.append(nd.ticker + '\n')

		append_dict = {}
		hash_table.write_list.append('\n\n\nShares with Shorts >= 15%:\n')
		for nd in hash_table.high_short_shares:
			if nd.shorts_percent_float >= 15:
				append_dict[nd.ticker] = nd.shorts_percent_float
		append_dict = sorted(append_dict.items(), key=operator.itemgetter(1), reverse=True)
		for val in append_dict:
			hash_table.write_list.append(str(str(val[0]) + '\t' + str(val[1]) + '\n'))

		# hash_table.write_list.append('\n\n\nShares with price uptrend for 4 or more days and near 52 week low:\n')
		hash_table.write_list.append('\n\n\nShares with price uptrend:\n')
		for nd in hash_table.pos_price_trend_list:
			# if nd in hash_table.good_yearly_low:
			hash_table.write_list.append(str(nd.ticker + '\n'))

		append_dict = {}
		hash_table.write_list.append('\n\n\nPossible Great Stocks (Short Pain, 4 Day Price Uptrend):\n')
		for nd in hash_table.watchlist:
			if nd.high_shorts and nd.price_uptrend:
				append_dict[nd] = nd.shorts_pain
		append_dict = sorted(append_dict.items(), key=operator.itemgetter(1), reverse=True)
		for val in append_dict:
			hash_table.write_list.append(str(str(val[0].ticker) + '\t' + str(val[1])) + '\t\t' + str(self.alt_price_uptrend(val[0])) + '\n')
		temp_dict = append_dict

		append_dict = {}
		hash_table.write_list.append(
			'\n\n\nThe Perfect Stocks (Positive Price, Volume Trend, High Short Shares Float. Does not Check Beta) (Short Pain, 4 Day Price Uptrend):\n')
		for nd in hash_table.pos_vol_trend_list:
			if nd not in temp_dict and nd.price_uptrend and nd in hash_table.high_short_shares:
				append_dict[nd] = nd.shorts_pain
		append_dict = sorted(append_dict.items(), key=operator.itemgetter(1), reverse=True)
		for val in append_dict:
			hash_table.write_list.append(str(str(val[0].ticker) + '\t' + str(val[1])) + '\t\t' + str(self.alt_price_uptrend(val[0])) + '\n')

		hash_table.write_list.append('\n\nTop 10 Stocks Experiencing Greatest Pain (Short Pain):\n')
		if len(hash_table.sorted_ranked_shares) < 10:
			for stock in hash_table.sorted_ranked_shares:
				hash_table.write_list.append(str(stock[0].ticker) + '\t' + str(stock[1]) + '\n')
		else:
			for stock in hash_table.sorted_ranked_shares[:10]:
				hash_table.write_list.append(str(stock[0].ticker) + '\t' + str(stock[1]) + '\n')

		self.write_to_file(hash_table)



	def write_to_file(self, hash_table):
		""" Writes all the print statements to a file automatically named by the date of next trading day. """

		next_date = self.next_open_date()

		year = next_date[0]
		month = next_date[1]
		day = next_date[2]

		filename = '../Watchlists/' + next_date[
			3] + '/' + month + '/Watchlists/watch_list_for_' + month + '_' + day + '_' + year + '.txt'

		with open(filename, 'w+') as f:
			for val in hash_table.write_list:
				f.write(val)



	def check_volume_trend(self, nd, page, hash_table):
		""" Checks the volume of the ticker sent in. If the volume is greater than 150% of the average volume, then the ticker
		will stay on the watchlist. Otherwise, it will be removed. """

		tr_list = page.findAll('tr')
		vol_to_beat = nd.avg_volume * 1.5

		prev_volume = 0
		vol_uptrend = 0
		vol_downtrend = 0

		# iterates through the volumes from the past 10 trading days
		trend_lst = []
		for i, tr in enumerate(reversed(tr_list[1:12])):
			try:
				volume = tr.findAll('td')[6].text
				volume = float(volume.replace(',', ''))
			except:
				return

			if volume > vol_to_beat:
				nd.days_twenty_perc_above_avg_volume += 1

			# only checks the most recent 6 days of trading for uptrend - edit this so that it is more specific and everything
			if i < 6:
				if prev_volume < volume:
					vol_uptrend += 1
					vol_downtrend = 0
					trend_lst.append(True)
				elif prev_volume > volume:
					vol_downtrend += 1
					trend_lst.append(False)

				# if >= two days trading with below prev_volume, everything is reset. vol_uptrend set to False
				if vol_downtrend >= 2:
					vol_uptrend = 0
					nd.vol_uptrend = False
				elif vol_uptrend >= 3:
					vol_downtrend = 0
					nd.vol_uptrend = True

			prev_volume = volume

		if not nd.vol_uptrend:
			for t in trend_lst[4:]:
				if not t:
					return
			nd.vol_uptrend = True

		# removes from watchlist if it has had fewer than 2 days above 120% average volume, otherwise appends to proper list
		if nd.days_twenty_perc_above_avg_volume < 2:
			hash_table.removed_list.append(nd)
			hash_table.watchlist.remove(nd)
		elif nd.vol_uptrend:
			hash_table.pos_vol_trend_list.append(nd)
		else:
			hash_table.neg_vol_trend_list.append(nd)



	def check_price_trend(self, nd, page, hash_table):
		""" Ensures the stock has had a positive price trend the previous 6 trading days. If it does, it will stay on
		the watchlist, otherwise it will be removed. """

		tr_list = page.findAll('tr')
		price_downtrend = 0

		try:
			prev_close = float(tr_list[7].findAll('td')[5].text)
		except:
			return

		# iterates through the most recent 6 trading days
		# Rules: it can only have 1 day not positive, the others MUST have consistent 5% increases
		for i, tr in enumerate(reversed(tr_list[1:4])):

			# safeguards against any failed price gather attempts
			try:
				close = float(tr.findAll('td')[5].text)
			except:
				return

			# performs the checks for price uptrend
			if close < (prev_close * 1.05):
				price_downtrend += 1
			if price_downtrend > 1:
				nd.price_uptrend = False

			prev_close = close

		# appends node to proper list
		if nd.price_uptrend and nd not in hash_table.pos_price_trend_list:
			hash_table.pos_price_trend_list.append(nd)



	def check_shorts_beta(self, nd, hash_table):
		""" Use the statistics tab on yahoo finance and grabs lots of numbers to do calculations. Also, float means total
		shares the company made available to the public. Outstanding shares is the total amount of shares held by EVERYONE. """

		# basically, just check if the short interest (short % of float) is above 5%
		ticker = nd.ticker
		cont = True

		page = nd.key_statistics_page

		i = 30
		nd.shorts_percent_float = 0

		# safeguards against a different position of the short shares percent
		while i < 52:
			try:
				if page.findAll('tr')[i].text[:16].strip() == 'Short % of Float':
					nd.shorts_percent_float = float(page.findAll('tr')[i].text[18:].replace('%', ''))
					break
			except:
				pass
			i += 1

		if nd.shorts_percent_float >= 15 and nd.perc_change >= 10:
			hash_table.high_shares_perc_change.append(nd)
		if nd.shorts_percent_float >= 5:
			hash_table.high_short_shares.append(nd)
			nd.high_shorts = True
		elif nd.shorts_percent_float < 5:
			hash_table.low_short_shares.append(nd)

		# checks beta here
		i = 20
		beta = 0

		# safeguards against a different position of the short shares percent
		while i < 52:
			try:
				if page.findAll('tr')[i].text[:4].strip() == 'Beta':
					beta = float(page.findAll('tr')[i].text[5:])
					break
			except:
				beta = 1.01
			i += 1

		if beta < 1 and beta > -1:
			hash_table.low_beta_lst.append(nd)
		else:
			hash_table.high_beta_lst.append(nd)
			nd.high_beta = True



	def check_yearly_low(self, nd, page, hash_table):
		""" Determines if the stock is within range of the yearly low. Assigns a weight to it based on this. """

		curr = page.findAll('tr')[5].text[13:]

		low = ''
		count = 0
		for char in curr:
			count += 1
			if char == ' ':
				break
			else:
				low += char

		try:
			high = float(curr[count + 1:].replace(',', ''))
			low = float(low)
			# if current price is within 35% of the low, where the 35% is based off the high
			if nd.curr_price <= (low * 1.35):
				hash_table.good_yearly_low.append(nd)
				nd.yearly_low = True
		except:
			return

		# calculation to determine what weight to assign it



	def check_pain(self, nd, hash_table):
		""" Ranks stocks that have the highest probability of a short squeeze. Salculates short percentage by percentage
			change in a day. Could also incorporate over a weekly basis, bring in other metrics, etc. Perhaps incorporate the
			amount of money the shorts have lost, too. """

		hash_table.ranked_shares[nd] = round((nd.shorts_percent_float * nd.perc_change), 3)
		nd.shorts_pain = round((nd.shorts_percent_float * nd.perc_change), 3)
		hash_table.sorted_ranked_shares = sorted(hash_table.ranked_shares.items(), key=operator.itemgetter(1), reverse=True)



	def alt_price_uptrend(self, nd):
		""" Returns True if there is an uptrend of 4 days in a row or more. False otherwise. """

		ticker = nd.ticker

		page = nd.main_page

		tr_list = page.findAll('tr')
		prev_close = 0

		# iterates through the most recent 4 trading days
		for i, tr in enumerate(reversed(tr_list[0:4])):
			# safeguards against any failed price-gather attempts
			try:
				close = float(tr.findAll('td')[5].text)
			except:
				break

			# performs the checks for price uptrend
			if close < (prev_close * 1.025):
				return False

			prev_close = close

		# appends node to price trend list
		return True



	def next_open_date(self):
		""" Returns the date of the next day the market is open to properly name the txt file. """

		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(days=1)

		# [month, day]
		closed_dates = [(1, 1), (1, 15), (2, 19), (3, 30), (5, 28), (7, 4), (9, 3), (11, 22), (12, 25)]

		time_delta = 1

		# tomorrow.weekday() returns int from 0-6, where 0 is Monday and 6 is Sunday
		if tomorrow.weekday() == 5:
			time_delta += 2
		elif tomorrow.weekday() == 6:
			time_delta += 1

		tomorrow = today + datetime.timedelta(days=time_delta)
		month = tomorrow.month
		day = tomorrow.day

		for date in closed_dates:
			if month == date[0] and day == date[1]:
				time_delta += 1

		tomorrow = today + datetime.timedelta(days=time_delta)

		year = str(tomorrow.year)[2:]
		month = str(tomorrow.month)
		day = str(tomorrow.day)

		# year, month, day, COMPLETE year
		ret_lst = [year, month, day, str(tomorrow.year), ]

		return ret_lst
