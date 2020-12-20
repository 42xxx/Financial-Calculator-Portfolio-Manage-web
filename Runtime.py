from time import perf_counter
import pandas as pd
from pandas import DataFrame
import yfinance as yf
import os
runtime_yf = []
runtime_csv = []
os.getcwd()
#runtimes using yfinance

djia = ['MMM', 'AXP', 'AMGN', 'AAPL', 'BA', 'CAT', 'CVX', 'CSCO', 'DOW',
         'GS', 'HON', 'IBM', 'INTC', 'JNJ', 'JPM', 'MCD', 'MRK', 'MSFT',
         'NKE', 'PG', 'CRM', 'KO', 'HD', 'TRV', 'DIS', 'UNH', 'VZ', 'V',
         'WBA', 'WMT']

results = []
for i in djia:
    j = djia.index(i)
    startTime = perf_counter()
    yf.download(i, start='2019-12-16', end='2020-12-17')
    endTime = perf_counter()
    yf2 = (endTime - startTime)
    if j > 1:
        yf2 = yf2 + results[(j - 1)]
    results.append(yf2)


runtime_yf = DataFrame(results, columns=['runtime'])
runtime_yf.reset_index(inplace=True)
runtime_yf = runtime_yf.rename(columns = {'index':'number of stocks'})
runtime_yf['number of stocks'] += 1


#runtimes using csv files

#For this project, we assume that the data is in
#the same directory as the .py file.

results = []
for i in djia:
    j = djia.index(i)
    startTime = perf_counter()
    filename = "data/"+i + ".csv"
    df = pd.read_csv(filename, encoding='utf-8')
    endTime = perf_counter()
    csv = (endTime - startTime)
    if j > 1:
        csv = csv + results[(j - 1)]
    results.append(csv)

runtime_csv = DataFrame(results, columns=['runtime'])
runtime_csv.reset_index(inplace=True)
runtime_csv = runtime_csv.rename(columns = {'index':'number of stocks'})
runtime_csv['number of stocks'] += 1

runtimes = []
runtimes = runtime_yf.join(runtime_csv, lsuffix='_yf', rsuffix='_csv')
runtimes = runtimes.rename(columns ={'number of stocks_yf':'number of stocks'})
runtimes.drop(columns=['number of stocks_csv'])