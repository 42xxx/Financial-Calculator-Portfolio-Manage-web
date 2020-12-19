from preloaded_data import preload
from app.py import user_rec
from pandas import pd

preload()
runtime_yf = []
runtime_csv = []

#runtimes using yfinance
startTime = datetime.now()
print(user_rec(50, 100, 1, 0.05, 'AAPL', '2019-12-16', '2020-12-17', option='put'))
yf1 = (datetime.now() - startTime)


djia = ['MMM', 'AXP', 'AMGN', 'AAPL', 'BA', 'CAT', 'CVX', 'CSCO', 'DOW',
         'GS', 'HON', 'IBM', 'INTC', 'JNJ', 'JPM', 'MCD', 'MRK', 'MSFT',
         'NKE', 'PG', 'CRM', 'KO', 'HD', 'TRV', 'DIS', 'UNH', 'VZ', 'V',
         'WBA', 'WMT']

results = []
startTime = datetime.now()

for i in djia:
    opt_px = user_rec(50, 100, 1, 0.05, i, '2019-12-16', '2020-12-17', option='put')
    results.append(opt_px)
yf2 = (datetime.now() - startTime)

runtime_yf.append(yf1, yf2)


#runtimes using csv files
startTime = datetime.now()
print(runtime(50, 100, 1, 0.05, 'AAPL', '2019-12-16', '2020-12-17', option='put'))
csv1 = (datetime.now() - startTime)

results = []
startTime = datetime.now()

for i in djia:
    opt_px = user_rec(50, 100, 1, 0.05, i, '2019-12-16', '2020-12-17', option='put')
    results.append(opt_px)
csv2 = (datetime.now() - startTime)

runtime_csv.append(yf1, yf2)

runtimes = pd.dataframe({'yf':runtime_yf,'csv':runtime_csv})