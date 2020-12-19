import yfinance as yf
import datetime
import numpy as np
import pandas as pd


class Portfolio:
	def __init__(self, tickers: list, observe_periods: int = 365):
		self.tickers = tickers
		self.tickers.append('SPY')
		self.period = observe_periods
		self.prices = pd.DataFrame(columns=self.tickers)
		self.returns = None
		self.rho = None
		self.Sigma = None
		self.betas = None

	def add_tickers(self, tickers: list):
		self.tickers.pop(-1)
		[self.tickers.append(i) for i in tickers]
		self.tickers.append('SPY')
		self.prices = pd.DataFrame(columns=self.tickers)

	def remove_tickers(self, tickers: list):
		for i in tickers:
			self.tickers.remove(i)
		self.prices = pd.DataFrame(columns=self.tickers)

	def prepare_data(self):
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
		info = pd.DataFrame(columns=self.tickers[:-1], index=["Beta(respect to 'SPY')", 'Expected return', 'volatility'])
		info.loc["Beta(respect to 'SPY')", :] = [round(i, 4) for i in self.betas[:-1]]
		info.loc['Expected return', :] = [round(i, 4) for i in self.rho[:-1]]
		info.loc['volatility', :] = [round(np.sqrt(i), 4) for i in np.diag(self.Sigma)[:-1]]
		return info

	def expect_return(self, weights):
		weights = weights / np.sum([np.abs(i) for i in weights])
		return self.rho[:-1].dot(weights)


if __name__ == '__main__':
	ticker_list = ['AAPL', 'BABA', 'CSCO', 'BE', 'JD', 'CNK', 'CRM', 'CHWY', 'JWN', 'PLUG']
	port = Portfolio([])
	port.add_tickers(ticker_list)
	port = Portfolio(ticker_list, 365)
	port.prepare_data()
	print(port.generate_df().T)



























