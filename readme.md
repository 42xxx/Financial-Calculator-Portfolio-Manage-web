
## FE 595 Final

\
\
**Purpose**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
A collaborative project between group members Yuwen Jin, Minghao Kang, Fangchi Wu, and Shiraz Bheda. Our purpose was to create a website with multiple features for options pricing, including user input, data visualization, and a comparison of runtime metrics that varies with source of historical data. The idea of this tool is that it will serve as a baseline for a potentially marketable product for end users who want to price out options quickly using their own assumptions in a clean and presentable web interface.
\
\
**Inspiration**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
We wanted to apply some of the skills we have learned in this class towards created fast and user-friendly financial tools. One of the main benefits of this project is that it has a lot of built-in user flexibility that allows for detailed results with a faster turnaround time than any simple solver-driven excel sheet can provide. Importantly, this is a project with high growth potential. It represents a baseline that is very scalable if the data is stored in a database, as opposed to downloading the necessary historical data from a package with every user request. Observing the differences in runtime helped in forming this conclusion and developing a product that is much more scalable.
\
\
**List of features for usage**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
1. Data visualization tools, including daily historical returns in a line plot and weekly or daily historical returns in a candlestick chart.
2. Detailed model feature selection, including model type, maturity type, and option type.
3. User-friendly input of spot price, strike price, time to maturity, and risk-free rate. Missing risk free rate will be replaced by the interest rate of one year US treasury bonds. 
4. Automatically calculates one year historical volatility for adjusted closing prices of the underlying asset.
5. Allow user to create and modify their own portfolio by inputting stock symbols and weights of the assets they want to investigate. The program will send back some basic information such as volatility and beta value  with respect to the market, represented by SPY.
\
\
**Deployment**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If a user wants to run this code on their own computer without publishing it for others to use, they will need to clone the code from our git and run it on their own desktop via the terminal. Once it is connected, a unique IP address will pop up, which can be copied and pasted into a browser. This will lead to the website, where the user can input data elements such as spot price, strike price, time to maturity, and risk-free rate. If the user wants to run this code and make it publicly available, then they will require an AWS instance or a similar service. 

1.Home page: The main page that launches from the python program. A user can either input option information and turn to the result page, or click the 'Manage your portfolio' button at the bottom of the page to explore the portfolio related functionality.
![image](https://github.com/StarryYJ/Financial-Cauculater/blob/master/IMG/home.jpg)
2.Results page: This page shows results and corresponding models/settings provided by the financial calculator.  
![image](https://github.com/StarryYJ/Financial-Cauculater/blob/master/IMG/result_1.jpg)
![image](https://github.com/StarryYJ/Financial-Cauculater/blob/master/IMG/result_2.png)
3.Portfolio page: When switching to this page for the first time, a user will input stock tickers to create a portfolio. Then there will be a textbox that will allow the user to add new tickers or remove existing ones. The program will return basic financial information regarding the tickers. Additionally, a user can type in the weights of each assets to see the total expected return.
![image](https://github.com/StarryYJ/Financial-Cauculater/blob/master/IMG/portfolio_re.jpg)
4.At the end of both the Results page and the Portfolio page, there is a 'back' button that allows the user to go back to the previous page.
\
\
**Next Steps**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Running a comparison on performance times for our function yielded a significant difference depending on where the data was pulled from. For this reason, we created a separate script, "Runtime", that is designed to measure the performance of downloading stock price data from the yfinance package of Python versus reading the data from a csv file. We found that pulling one year of historical data for a stock takes ~0.33 seconds. The performance was incrementally scaled using the list of stocks in the Dow Jones Index, with the total time for the entire list taking ~9 seconds. This is unacceptable for a project that is designed to scale. By contrast, pulling the data of a single stock by reading a csv file took .11 seconds. Incremental increases in reading .csv did not add significant incremental time; the entire list of Dow Jones industry stocks took .15 seconds. Based on this analysis, we believe that the latter source can help scale the project by increasing the number of options that can be priced quickly. A difference of several seconds can mean everything for market traders who would be interested in using such a tool, since this group values speed and quick execution when chasing rallies or selling fades. We believe that faster performance times can be one of the most marketable selling points for this product.

In addition, the portfolio management component can also be improved upon in many ways, such as adding generalizations or improving error detection.
