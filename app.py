from flask import Flask, render_template, request, url_for, flash
import pandas as pd
import numpy as np
import os
import yfinance as yf
import itertools
from commonoption import *
import quandl
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.pylab import date2num
import urllib
from io import BytesIO
import base64
from lxml import etree
import random
import datetime
from pyecharts.charts import Kline
import mpl_finance as mpf


app = Flask(__name__)
quandl.ApiConfig.api_key = "ASwbrrw4mXfhBSMWrEtp"
risk_free = quandl.get('FRED/DGS1', authtoken="ASwbrrw4mXfhBSMWrEtp").iloc[-1, 0]

today = datetime.date.today()
formatted_today = today.strftime('%Y-%m-%d')
one_year = today + datetime.timedelta(days=-365)
formatted_one_year = one_year.strftime('%Y-%m-%d')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/result', methods=['POST', 'GET'])
def user_rec():
    pricing_model = request.form.getlist('pricing_model')
    option_type = request.form.getlist('option_type')
    ticker, S, K, r, T = read_in()
    try:
        adj_close = yf.download(ticker, start=formatted_one_year, end=formatted_today)['Adj Close']
    except ValueError("There's not enough data."):
        adj_close = yf.download(ticker)['Adj Close']
    fig = plt.figure(figsize=(12, 8), dpi=100, facecolor="white")
    plt.title('Adjusted close of ' + ticker)
    plt.plot(adj_close, color='darkseagreen')
    plt.xlabel('Date')
    plt.ylabel('Price')
    sio = BytesIO()
    fig.savefig(sio, format='png')
    data = base64.encodebytes(sio.getvalue()).decode()
    adj_plot = 'data:image/png;base64,' + str(data)

    sio = BytesIO()
    if request.form.get('candle_stick') == 'day':
        candle_fig = candle_stick(ticker)
    else:
        candle_fig = candle_stick(ticker, 'week')
    candle_fig.savefig(sio, format='png')
    data = base64.encodebytes(sio.getvalue()).decode()
    cs_plot = 'data:image/png;base64,' + str(data)

    result_df = pd.DataFrame(columns=['model', 'option type', 'Expected PRICE'])
    title, prices, model, o_type, BS_bool, BS_df, BS_html = [], [], [], [], False, None, None
    call = CommonOption(call_or_put=1, maturity=T/365, spot_price=S,
                        sigma=float(np.std(adj_close.diff()[1:]/adj_close[:-1]) * np.sqrt(252)),
                        risk_free_rate=r, strike_price=K, dividends=0)
    put = CommonOption(call_or_put=0, maturity=T/365, spot_price=S,
                       sigma=float(np.std(adj_close.diff()[1:]/adj_close[:-1]) * np.sqrt(252)),
                       risk_free_rate=r, strike_price=K, dividends=0)

    if 'BS model' in pricing_model:
        BS_bool = True
        model = ['BS model']*2
        o_type = ['European Option']*2
        pricing_model.remove('BS model')
        BS_df = pd.DataFrame(columns=['delta', 'gamma', 'vega', 'theta', 'rho'], index=['call', 'put'])
        BS_df.iloc[0, :] = call.B_S_call_para()[1:]
        BS_df.iloc[1, :] = call.B_S_put_para()[1:]
    combination = list(itertools.product(pricing_model, option_type))

    [model.append(i) for i in np.array([[i[0]]*2 for i in combination]).flatten()]
    [o_type.append(i) for i in np.array([[i[1]]*2 for i in combination]).flatten()]
    result_df['model'] = np.array(model).flatten()
    result_df['option type'] = np.array(o_type).flatten()

    for i in range(int(result_df.shape[0])):
        if i % 2 == 0:
            title.append(ticker + ' ' + str(T) + ' day(s) call')
            prices.append(fit_model(result_df['model'][i], result_df['option type'][i], call))
        else:
            title.append(ticker + ' ' + str(T) + ' day(s) put')
            prices.append(fit_model(result_df['model'][i], result_df['option type'][i], put))
    result_df.index = title
    result_df['Expected PRICE'] = prices

    return render_template('result.html', result=result_df, BS_bool=BS_bool,
                           BS_df=BS_df, adj_plt=adj_plot, candle_plt=cs_plot)


def read_in():
    ticker = request.form['ticker']
    try:
        S = float(request.form['S'])
    except ValueError('Please enter a number'):
        S = -1
    try:
        K = float(request.form['K'])
    except ValueError('Please enter a number'):
        K = -1
    try:
        r = float(request.form['r'])
    except:
        r = risk_free
    try:
        T = float(request.form['T'])
    except ValueError('Please enter a number'):
        T = -1
    return ticker, S, K, r, T


def run_time():
    S = request.form['S']
    K = request.form['K']
    r = request.form['r']
    T = request.form['T']
    return S, K, r, T


def fit_model(model, option_type, option: CommonOption):
    price = -1
    if model == 'BS model':
        price = option.B_S()
    if model == 'Binomial Tree' and option_type == 'European Option':
        price = option.binomial_tree_EU(3)[0]
    elif model == 'Binomial Tree' and option_type == 'American Option':
        price = option.binomial_tree_US(3)[0]
    if model == 'Trinomial Tree' and option_type == 'European Option':
        price = option.trinomial_tree_EU(3)[0]
    elif model == 'Trinomial Tree' and option_type == 'American Option':
        price = option.trinomial_tree_US(3)[0]
    return round(price, 4)


def candle_stick(stock, period='day'):
    if period == "week":
        start = today + datetime.timedelta(days=-500)
        formatted_start = start.strftime('%Y-%m-%d')
        try:
            prices_row = yf.download(stock, start=formatted_start, end=formatted_today)
        except ValueError("There's not enough data."):
            prices_row = yf.download(stock)
        days = prices_row.index

        weekdays = []
        stamp = []
        temp_day = days[0]
        while temp_day < datetime.datetime.strptime(formatted_today, '%Y-%m-%d'):
            if temp_day in days:
                weekdays.append(int(temp_day.strftime("%w")))
            temp_day += datetime.timedelta(days=1)

        for i in range(len(weekdays)-1):
            if weekdays[i+1] < weekdays[i]:
                stamp.append(i)

        prices_row['help_col'] = range(len(prices_row))
        prices_row['help_col_1'] = range(len(prices_row))
        for i in stamp:
            prices_row.loc[prices_row['help_col'] >= i, ['help_col_1']] = i
        prices_row.loc[prices_row['help_col'] <= stamp[0], ['help_col_1']] = 0

        group = prices_row.groupby('help_col_1')
        prices = group.agg({'High': 'max', 'Low': 'min', 'Open': lambda x: x[0],
                            'Close': lambda x: x[-1]})

        if stamp[0] == 0:
            prices.index = list(days[stamp])
        else:
            prices.index = [days[0]] + list(days[stamp])

        title = 'Weekly Candle Stick of ' + stock
    else:
        half_year = today + datetime.timedelta(days=-180)
        formatted_half_year = half_year.strftime('%Y-%m-%d')
        try:
            prices = yf.download(stock, start=formatted_half_year, end=formatted_today)
        except ValueError("There's not enough data."):
            prices = yf.download(stock)
        title = 'Daily Candle Stick of ' + stock

    # Initial settings of the figure and subplot
    fig = plt.figure(figsize=(12, 8), dpi=100, facecolor="white")
    fig.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
    graph_KAV = fig.add_subplot(1, 1, 1)

    # plot the candle sticks
    mpf.candlestick2_ochl(graph_KAV, prices.Open, prices.Close, prices.High, prices.Low,
                          width=0.8, colorup='darkseagreen', colordown='indianred')

    # get moving averages and add the lines to the plot
    prices['Ma20'] = prices.Close.rolling(window=20).mean()
    prices['Ma30'] = prices.Close.rolling(window=30).mean()
    graph_KAV.plot(np.arange(0, len(prices.index)), prices['Ma20'], 'mediumpurple', label='M20', lw=1.0)
    graph_KAV.plot(np.arange(0, len(prices.index)), prices['Ma30'], 'orange', label='M30', lw=1.0)

    # other settings such as legends
    graph_KAV.legend(loc='best')
    graph_KAV.set_title(title)
    graph_KAV.set_xlabel("Date")
    graph_KAV.set_ylabel("Price")
    graph_KAV.set_xlim(0, len(prices.index))
    # x-labels setting
    graph_KAV.set_xticks(range(0, len(prices.index), 15))
    graph_KAV.set_xticklabels([prices.index.strftime('%Y-%m-%d')[index] for index in graph_KAV.get_xticks()])

    return fig


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
