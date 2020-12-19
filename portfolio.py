import yfinance as yf
import pandas as pd
import numpy as np
import datetime


class Portfolio:
	def __init__(self, ticker_list: list, observe_periods: int):
		self.tickers = ticker_list
		self.period = observe_periods
		self.prices = pd.DataFrame(columns=self.tickers)
		self.returns = None
		self.rho = None
		self.Sigma = None
		self.betas = None
		self.market = {'price':[], 'returns':[],'var':None}

	def prepare_data(self):
		today = datetime.date.today()
		formatted_today = today.strftime('%Y-%m-%d')
		one_year = today + datetime.timedelta(days=-365)
		formatted_one_year = one_year.strftime('%Y-%m-%d')
		self.market['price'] = yf.download('SPY', start=formatted_one_year, end=formatted_today)
		self.market['returns'] = np.diff(self.market['price'])[1:]/self.market['price'][:-1]
		self.market['var'] = [np.var(self.market['returns'])]
		for ticker in self.tickers:
			self.prices[ticker] = yf.download(ticker, start=formatted_one_year, end=formatted_today)
		self.returns = self.prices.apply(lambda x:x.diff()[1:]/x[:-1], axis=1)
		self.rho = self.returns.apply(np.mean)
		self.Sigma = np.cov(self.returns.T)
		self.betas = []  # beta of each ticker
		for i in range(len(self.rho)):
			self.betas.append(np.cov(self.returns.iloc[:, i],
									 self.market['returns'])[0, 1] / self.market['var'])

	def calculate_beta(self):
		pass


if __name__=='__main__':
	pass




























