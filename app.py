from flask import Flask, render_template, request, flash
from flask_session import Session
import itertools
from commonoption import *
import quandl
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import mpl_finance as mpf
from portfolio import *
import os


# Initialize
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
Session(app)
quandl.ApiConfig.api_key = "ASwbrrw4mXfhBSMWrEtp"
risk_free = quandl.get('FRED/DGS1', authtoken="ASwbrrw4mXfhBSMWrEtp").iloc[-1, 0]

today = datetime.date.today()
formatted_today = today.strftime('%Y-%m-%d')
one_year = today + datetime.timedelta(days=-365)
formatted_one_year = one_year.strftime('%Y-%m-%d')

port = Portfolio([])
info_df = None


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/result', methods=['POST', 'GET'])
def user_rec():
    """
    Using for basic functionality of the financial calculator

    :return: to the result page of basic financial calculator results
    """
    pricing_model = request.form.getlist('pricing_model')
    option_type = request.form.getlist('option_type')
    ticker = request.form['ticker']

    # input error detect
    if request.method == 'POST':
        err_index = []
        skrt = [request.form['S'], request.form['K'], request.form['r'], request.form['T']]
        try:
            a = yf.download(ticker, start="2019-12-01", end="2020-12-01")['Adj Close']
        except ValueError:
            a = 1
        if len(a) == 0:
            err_index.append(1)
            flash('Your input is not a Ticker(symbol) listed in yahoo finance', 'ticker')
        for i in range(len(skrt)):
            try:
                skrt[i] = float(skrt[i])
            except ValueError:
                err_index.append(i + 2)
                flash(u'Your input {0} is not a number'.format(['S', 'K', 'r', 'T'][i]), ['S', 'K', 'risk', 'T'][i])
        if len(pricing_model) == 0:
            err_index.append(6)
            flash(u'You must choose at least one among the 3 methods', 'model')
        if len(option_type) == 0:
            err_index.append(7)
            flash(u'You must choose at least one among the 2 option types', 'type')
        if request.form.get('candle_stick') is None:
            err_index.append(8)
            flash(u'You must choose one among these 2.', 'period')
        if len(err_index) == 0:
            pass
        else:
            # back to the home page together with error description
            return render_template('home.html')

    # the formal calculation part
    S, K, r, T = read_in()
    # using one year historical data to calculate volatility and plot price trend chart
    try:
        adj_close = yf.download(ticker, start=formatted_one_year, end=formatted_today)['Adj Close']
    except ValueError("There's not enough data."):
        adj_close = yf.download(ticker)['Adj Close']

    # plot price trend chart and show it on the web page
    fig = plt.figure(figsize=(12, 8), dpi=100, facecolor="white")
    plt.title('Adjusted close of ' + ticker)
    plt.plot(adj_close, color='darkseagreen')
    plt.xlabel('Date')
    plt.ylabel('Price')
    sio = BytesIO()
    fig.savefig(sio, format='png')
    data = base64.encodebytes(sio.getvalue()).decode()
    adj_plot = 'data:image/png;base64,' + str(data)

    # plot candle stick chart and show it on the web page
    sio = BytesIO()
    if request.form.get('candle_stick') == 'day':
        candle_fig = candle_stick(ticker)
    else:
        candle_fig = candle_stick(ticker, 'week')
    candle_fig.savefig(sio, format='png')
    data = base64.encodebytes(sio.getvalue()).decode()
    cs_plot = 'data:image/png;base64,' + str(data)

    # format a pandas data frame to store the pricing results together with methods and some other info
    result_df = pd.DataFrame(columns=['model', 'option type', 'Expected PRICE'])
    title, prices, model, o_type, BS_bool, BS_df, BS_html = [], [], [], [], False, None, None
    call = CommonOption(call_or_put=1, maturity=T/365, spot_price=S,
                        sigma=float(np.std(adj_close.diff()[1:]/adj_close[:-1]) * np.sqrt(252)),
                        risk_free_rate=r, strike_price=K, dividends=0)
    put = CommonOption(call_or_put=0, maturity=T/365, spot_price=S,
                       sigma=float(np.std(adj_close.diff()[1:]/adj_close[:-1]) * np.sqrt(252)),
                       risk_free_rate=r, strike_price=K, dividends=0)

    comb_mess = 0
    if 'BS model' in pricing_model and 'American Option' in option_type:
        comb_mess = 'BS model currently does not support American Option pricing in this project.'

    # create another table for option parameters calculated with Black Shore model
    if 'BS model' in pricing_model:
        BS_bool = True
        model = ['BS model']*2
        o_type = ['European Option']*2
        pricing_model.remove('BS model')
        BS_df = pd.DataFrame(columns=['delta', 'gamma', 'vega', 'theta', 'rho'], index=['call', 'put'])
        BS_df.iloc[0, :] = call.B_S_call_para()[1:]
        BS_df.iloc[1, :] = call.B_S_put_para()[1:]

    # mapping all combinations of financial model and option type
    combination = list(itertools.product(pricing_model, option_type))

    # format the result data frame
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

    # link to the result web page
    return render_template('result.html', result=result_df, BS_bool=BS_bool,
                           BS_df=BS_df, adj_plt=adj_plot, candle_plt=cs_plot, comb_mess=comb_mess)


@app.route('/portfolio', methods=['POST', 'GET'])
def manage_portfolio():
    """
    Using for functionality associated with portfolio

    :return:link to the portfolio page
    """
    global port, info_df
    exp_ret, weight_df = ['empty']*2
    n = len(port.tickers)
    try:
        ticker_add = request.form['add tickers']
        if ',' in ticker_add:
            tickers = [i.lstrip().lstrip("'").rstrip().rstrip("'") for i in ticker_add.split(',')]
        else:
            tickers = ticker_add.strip()
        port.add_tickers(tickers)
        port.prepare_data()
        info_df = port.generate_df()
    except:
        pass

    if n > 1:
        if 'remove tickers' in request.args.keys():
            ticker_remove = request.form['remove tickers']
            try:
                if ',' in ticker_remove:
                    tickers = [i.lstrip().lstrip("'").rstrip().rstrip("'") for i in ticker_remove.split(',')]
                else:
                    tickers = ticker_remove.strip()
                port.remove_tickers(tickers)
                port.prepare_data()
                info_df = port.generate_df()
            except:
                pass
        if 'option weights' in request.args.keys():
            weights_in = request.form['option weights']
            try:
                weights = [i.lstrip().rstrip() for i in weights_in.split(',')]
                weights = [float(i) for i in weights]
                exp_ret = round(port.expect_return(weights), 4)
            except ValueError:
                return render_template('portfolio.html', info_df=info_df, n=len(port.tickers),
                                       exp_ret=exp_ret, weight_df=weight_df)

        weight_df = pd.DataFrame(columns=['ticker', 'weights'])
        weight_df['ticker'] = port.tickers[:-1]
        weight_df['weights'] = port.weights
    return render_template('portfolio.html', info_df=info_df, n=len(port.tickers), exp_ret=exp_ret, weight_df=weight_df)


def read_in():
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
    return S, K, r, T


def fit_model(model, option_type, option: CommonOption):
    """
    It's made to simplify functions with decoration

    :param model: a financial model that is to be used
    :param option_type: Option type that needed to be considered
    :param option: the initialized CommonOption class object
    :return: estimated price of the option
    """
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
    """
    A function to generate candle stick chart with given stock symbol and time period of a single stick.
    For weekly chart use latest 500 days price information and for daily, use the last half year's data.

    :param stock:stock symbol
    :param period:to generate daily chart or weekly, input 'day' or 'week
    :return:the plot object generated by matplotlib.pyplot
    """
    if period == "week":
        start = today + datetime.timedelta(days=-500)
        formatted_start = start.strftime('%Y-%m-%d')
        try:
            prices_row = yf.download(stock, start=formatted_start, end=formatted_today)
        except ValueError("There's not enough data."):
            prices_row = yf.download(stock)
        days = prices_row.index

        # to make groups of data in order to find prices of every single sticks
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
