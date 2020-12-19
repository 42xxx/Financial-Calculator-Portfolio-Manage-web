import yfinance as yf
import datetime
import numpy as np
import pandas as pd


class Portfolio:
	def __init__(self, tickers: list, observe_periods: int = 365):
		"""
		To generate a Portfolio class object

		:param tickers: a list of stock symbols
		:param observe_periods:the days of the period that you put as your observation
		"""
		self.tickers = tickers.copy()
		self.tickers.append('SPY')
		self.period = observe_periods
		self.prices = pd.DataFrame(columns=self.tickers)
		self.returns = None
		self.rho = None
		self.Sigma = None
		self.betas = None
		self.weights = None

	def add_tickers(self, tickers: list):
		"""
		Allow user to manage the portfolio by adding new tickers

		:param tickers: a list of stock symbols
		:return: None
		"""
		self.tickers.pop(-1)
		if type(tickers) is list:
			[self.tickers.append(i) for i in tickers]
		elif type(tickers) is str:
			if tickers != '':
				self.tickers.append(tickers)
		self.tickers = list(set(self.tickers))
		self.tickers.append('SPY')
		self.prices = pd.DataFrame(columns=self.tickers)

	def remove_tickers(self, tickers: list):
		"""
		Allow user to manage the portfolio by removing existing tickers

		:param tickers: a list of stock symbols
		:return:
		"""
		if type(tickers) is list:
			for i in tickers:
				self.tickers.remove(i)
		elif type(tickers) is str:
			self.tickers.remove(tickers)
		self.prices = pd.DataFrame(columns=self.tickers)

	def prepare_data(self):
		"""
		Download data from yahoo finance

		:return: None, but will store data inside the class object
		"""
		today = datetime.date.today()
		formatted_today = today.strftime('%Y-%m-%d')
		one_year = today + datetime.timedelta(days=-self.period)
		formatted_one_year = one_year.strftime('%Y-%m-%d')
		for ticker in self.tickers:
			self.prices[ticker] = yf.download(ticker, start=formatted_one_year, end=formatted_today)['Adj Close'].dropna()
		self.returns = self.prices.apply(lambda x: x.diff()/x[:-1] * np.sqrt(252), axis=0).dropna()
		self.rho = self.returns.apply(np.mean)
		self.Sigma = np.cov(self.returns.T)
		self.betas = []  # beta of each ticker
		for i in range(len(self.rho)):
			self.betas.append(np.cov(self.returns.iloc[:, i],
									 self.returns.iloc[:, -1])[0, 1] / self.Sigma[-1, -1])

	def generate_df(self):
		"""
		Creates a data frame that describes some basic information of stocks in current portfolio
		:return:
		"""
		info = pd.DataFrame(columns=self.tickers[:-1], index=["Beta(respect to 'SPY')", 'Expected return', 'volatility'])
		info.loc["Beta(respect to 'SPY')", :] = [round(i, 4) for i in self.betas[:-1]]
		info.loc['Expected return', :] = [round(i, 4) for i in self.rho[:-1]]
		info.loc['volatility', :] = [round(np.sqrt(i), 4) for i in np.diag(self.Sigma)[:-1]]
		return info

	def expect_return(self, weights):
		"""
		Calculate expected return of current portfolio with given investing weights
		:param weights: a list telling how much you'll invest on each stock
		:return: expected return of current portfolio
		"""
		self.weights = weights / np.sum([np.abs(i) for i in weights])
		return self.rho[:-1].dot(self.weights)


if __name__ == '__main__':
	ticker_list = ['AAPL', 'BABA', 'CSCO', 'BE', 'JD', 'CNK', 'CRM', 'CHWY', 'JWN', 'PLUG']
	port = Portfolio([])
	port.add_tickers(ticker_list)
	port.prepare_data()
	print(port.generate_df().T)

















