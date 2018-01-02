class Node:

    def __init__(self, ticker, name, prev_close, open_p, curr):
        self.next = None
        self.prev = None
        self.ticker = ticker
        self.name = name
        self.prev_close = prev_close
        self.open = open_p
        self.curr = curr
        self.perc_change = 0
        self.avg_volume = 0
        self.vol_uptrend = True
        self.price_uptrend = True
        self.high_shorts = False
        self.high_beta = False
        self.days_twenty_perc_above_avg_volume = 0
        self.shorts_percent_float = 0
        self.shorts_pain = 0
        self.days_to_cover = 0

    def get_ticker(self):
        return self.ticker

    def get_next(self):
        return self.next

    def get_prev(self):
        return self.prev

    def get_name(self):
        return self.name

    def get_prev_close(self):
        return self.prev_close

    def get_open(self):
        return self.open

    def set_ticker(self, ticker):
        self.ticker = ticker

    def set_name(self, name):
        self.name = name

    def set_next(self, new_next):
        self.next = new_next

    def set_prev(self, new_prev):
        self.prev = new_prev

    def set_prev_close(self, close):
        self.prev_close = close

    def set_open(self, open_p):
        self.open = open_p

    def set_close(self, close):
        self.close = close

"""    def add_to_days_above_twenty(self):
        self.days_twenty_perc_above_avg_volume += 1"""
