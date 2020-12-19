import pandas as pd
import numpy as np
from scipy.stats import norm
from autograd import grad
import scipy


class CommonOption:
	"""
	define a class to store common option data and function definition
	"""

	# if call_or_put == 1, means call option, else, put option.

	def __init__(self, call_or_put, maturity, spot_price, sigma, risk_free_rate, strike_price, dividends):
		self.I = call_or_put
		self.T = maturity
		self.S0 = spot_price
		self.sigma = sigma
		self.r = risk_free_rate
		self.K = strike_price
		self.q = dividends

	# define a function to create binomial_tree of European option
	def binomial_tree_EU(self, N):
		"""
		input: the option and the number of periods
		output: the binomial tree of this option (matrix)
		"""

		# parameter initializing
		dt, u = self.T / N, np.exp(self.sigma * np.sqrt(self.T / N))
		d = 1 / u;
		p = (np.exp((self.r - self.q) * dt) - d) / (u - d)

		# ------------------ underlying price tree part ------------------ #
		# create an empty (N+1, N+1) matrix to store underlying stock price.
		underlying_price_tree = np.zeros([N + 1, N + 1])

		# forward step to calculate the underlying stock price
		# The upper trigonometric part of the matrix is useful
		for i in range(N + 1):
			for j in range(i + 1):
				underlying_price_tree[j, i] = self.S0 * (d ** j) * (u ** (i - j))

		# -------------------- option price tree part -------------------- #
		# create an empty (N+1, N+1) matrix to store option price.
		option_price_tree = np.zeros([N + 1, N + 1])

		# calculate the option price on maturity date (the last column of the matrix)
		# backward step to calculate the option price before the maturity
		option_price_tree[:, N] = np.maximum(np.zeros(N + 1),
											 (underlying_price_tree[:, N] - self.K) * (-1 + 2 * self.I))
		for i in np.arange(N - 1, -1, -1):
			for j in np.arange(0, i + 1):
				option_price_tree[j, i] = np.exp(-self.r * dt) * (
						p * option_price_tree[j, i + 1] + (1 - p) * option_price_tree[j + 1, i + 1])

		# ------------------- function return ---------------------------- #
		# output a list, containing spot option price, the underlying price tree, the option price tree
		return [option_price_tree[0, 0], np.round(underlying_price_tree, 2), np.round(option_price_tree, 2)]

	# define a function to create binomial_tree of American option
	def binomial_tree_US(self, N):
		[EU_option_tree, EU_underlying_tree] = [self.binomial_tree_EU(N)[2], self.binomial_tree_EU(N)[1]]

		dt, u = self.T / N, np.exp(self.sigma * np.sqrt(self.T / N))
		d = 1 / u
		p = (np.exp((self.r - self.q) * dt) - d) / (u - d)

		# this tree records if exercise the option at any time.
		US_option_tree = EU_option_tree
		for i in range(N - 1, -1, -1):
			for j in np.arange(0, i + 1):
				US_option_tree[j, i] = np.exp(-self.r * dt) * (
						p * US_option_tree[j, i + 1] + (1 - p) * US_option_tree[j + 1, i + 1])
			US_option_tree[0:(i + 1), i] = np.maximum(US_option_tree[0:(i + 1), i],
													  ((EU_underlying_tree - self.K) * self.I)[0:(i + 1), i])
		# US option has the right to exercise before the maturity day
		return [US_option_tree[0, 0], np.round(US_option_tree, 2)]

	def trinomial_tree_EU(self, N):
		"""
		input: the option and the number of periods
		output: the trinomial tree of this option (matrix)
		"""

		# parameter initializing
		dt, u = self.T / N, np.exp(self.sigma * np.sqrt(3 * self.T / N))
		d = 1 / u
		p_d = - (np.sqrt(dt / (12 * self.sigma * self.sigma))) * (
				self.r - self.q - 0.5 * self.sigma * self.sigma) + 1 / 6
		p_m = 2 / 3;
		p_u = (np.sqrt(dt / (12 * self.sigma * self.sigma))) * (self.r - self.q - 0.5 * self.sigma * self.sigma) + 1 / 6

		# ------------------ underlying price tree part ------------------ #
		# create an empty (2*N+1, N+1) matrix to store underlying stock price.
		underlying_price_tree = np.zeros([2 * N + 1, N + 1])

		# forward step to calculate the underlying stock price
		underlying_price_tree[N, :] = self.S0
		for i in range(1, N + 1):
			for j in range(1, i + 1):
				underlying_price_tree[N - j, i] = underlying_price_tree[N + 1 - j, i - 1] * u
				underlying_price_tree[N + j, i] = underlying_price_tree[N - 1 + j, i - 1] * d

		# -------------------- option price tree part -------------------- #
		# create an empty (N+1, N+1) matrix to store option price.
		option_price_tree = np.zeros([2 * N + 1, N + 1])

		# calculate the option price on maturity date (the last column of the matrix)
		# backward step to calculate the option price before the maturity
		option_price_tree[:, N] = np.maximum(np.zeros(2 * N + 1),
											 (underlying_price_tree[:, N] - self.K) * (-1 + 2 * self.I))
		for i in np.arange(N - 1, -1, -1):
			for j in np.arange(-i, i + 1):
				option_price_tree[N + j, i] = np.exp(-self.r * dt) * (
						p_m * option_price_tree[N + j, i + 1] + p_d * option_price_tree[N + j + 1, i + 1] +
						p_u * option_price_tree[N + j - 1, i + 1])

		# ------------------- function return ---------------------------- #
		# output a list, containing spot option price, the underlying price tree, the option price tree
		return [option_price_tree[N, 0], np.round(underlying_price_tree, 2), np.round(option_price_tree, 2)]

	def trinomial_tree_US(self, N):
		[EU_option_tree, EU_underlying_tree] = [self.trinomial_tree_EU(N)[2], self.trinomial_tree_EU(N)[1]]

		dt, u = self.T / N, np.exp(self.sigma * np.sqrt(3 * self.T / N));
		d = 1 / u
		p_d = - (np.sqrt(dt / (12 * self.sigma * self.sigma))) * (
				self.r - self.q - 0.5 * self.sigma * self.sigma) + 1 / 6
		p_m = 2 / 3;
		p_u = (np.sqrt(dt / (12 * self.sigma * self.sigma))) * (self.r - self.q - 0.5 * self.sigma * self.sigma) + 1 / 6

		# this tree records if exercise the option at any time.
		US_option_tree = EU_option_tree
		for i in range(N - 1, -1, -1):
			for j in np.arange(-i, i + 1):
				US_option_tree[N + j, i] = np.exp(-self.r * dt) * (
						p_m * US_option_tree[N + j, i + 1] + p_d * US_option_tree[N + j + 1, i + 1] +
						p_u * US_option_tree[N + j - 1, i + 1])
			US_option_tree[:, i] = np.maximum(US_option_tree[:, i], ((EU_underlying_tree - self.K) * self.I)[:, i])
		# US option has the right to exercise before the maturity day
		return [US_option_tree[N, 0], np.round(US_option_tree, 2)]

	# Use Black-Scholes formula calculate the option price
	def B_S(self):
		F = np.exp((self.r - self.q) * self.T)
		d1 = (np.log(self.S0 / self.K) + (self.r + self.sigma ** 2 / 2) * self.T) / (self.sigma * np.sqrt(self.T))
		d2 = d1 - self.sigma * np.sqrt(self.T)
		N = norm.cdf

		if self.I == 1:
			return self.S0 * np.exp(-self.q * self.T) * N(d1) - self.K * np.exp(-self.r * self.T) * N(d2)
		else:
			return self.K * np.exp(-self.r * self.T) * N(-d2) - self.S0 * np.exp(-self.q * self.T) * N(-d1)

	def B_S_call_para(self):
		d1 = (np.log(self.S0 / self.K) + (self.r + self.sigma ** 2 / 2) * self.T) / (self.sigma * np.sqrt(self.T))
		d2 = d1 - self.sigma * np.sqrt(self.T)
		N = norm.cdf
		M = norm.pdf
		c = self.S0 * np.exp(-self.q * self.T) * N(d1) - self.K * np.exp(-self.r * self.T) * N(d2)
		delta = round(N(d1), 4)
		gamma = round(M(d1) / (self.sigma * self.S0 * np.sqrt(self.T)), 4)
		vega = self.S0 * M(d1) * np.sqrt(self.T) * 0.01
		theta = (- self.S0 * M(d1) * self.sigma / (2 * np.sqrt(self.T)) - self.r * self.K * np.exp(
			-self.r * self.T) * N(d2)) / 365
		rho = self.K * self.T * np.exp(-self.r * self.T) * N(d2) / 100

		return round(c, 4), round(delta, 4), round(gamma, 4), round(vega, 4), round(theta, 6), round(rho, 4)

	def B_S_put_para(self):
		d1 = (np.log(self.S0 / self.K) + (self.r + self.sigma ** 2 / 2) * self.T) / (self.sigma * np.sqrt(self.T))
		d2 = d1 - self.sigma * np.sqrt(self.T)
		N = norm.cdf
		M = norm.pdf
		p = self.K * np.exp(-self.r * self.T) * N(-d2) - self.S0 * np.exp(-self.q * self.T) * N(-d1)
		delta = np.exp(-self.q * self.T) * round(N(d1) - 1, 4)
		gamma = round(M(d1) / (self.sigma * self.S0 * np.sqrt(self.T)), 4)
		theta = (- self.S0 * M(d1) * self.sigma / (2 * np.sqrt(self.T)) + self.r * self.K * np.exp(
			-self.r * self.T) * N(-d2)) / 365
		vega = self.S0 * M(d1) * np.sqrt(self.T) * 0.01
		rho = -self.K * self.T * np.exp(-self.r * self.T) * N(-d2) / 100

		return round(p, 4), round(delta, 4), round(gamma, 4), round(vega, 4), round(theta, 6), round(rho, 4)


if __name__ == '__main__':
	option1 = CommonOption(call_or_put=1, maturity=0.5, spot_price=60, sigma=0.25,
							risk_free_rate=0.05, strike_price=60, dividends=0)
	print(option1.trinomial_tree_EU(3)[0])
	print(option1.trinomial_tree_US(3)[0])

	option1 = CommonOption(call_or_put=0, maturity=0.25, spot_price=60, sigma=0.25,
							risk_free_rate=0.05, strike_price=60, dividends=0)
	option1.binomial_tree_EU(3)

	option1 = CommonOption(call_or_put=1, maturity=1, spot_price=30, sigma=0.25,
							risk_free_rate=0.06, strike_price=30, dividends=0)
	option1.B_S_call_para()

	# Test option: which is in Example 21.1 in HULL book.
	option1 = CommonOption(call_or_put=0, maturity=1 / 3, spot_price=30, sigma=0.25,
							risk_free_rate=0.05, strike_price=29, dividends=0)
	option1.B_S()

	# same result in the book if we set call_or_put = 1)
	option1.binomial_tree_US(5)

	option1.binomial_tree_EU(5)

	# when N --> ∞ , the price approaches the price given by the Black-Scholes formula
	print(option1.binomial_tree_EU(99)[0])

