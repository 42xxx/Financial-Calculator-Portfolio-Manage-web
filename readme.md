
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
3. User-friendly input of spot price, strike price, time to maturity, and risk-free rate.
4. Automatically calculates one year historical volatility for adjusted closing prices of the underlying asset.
5. Allow user to create and modify their own portfolio by inputting stock symbols and weights of the assets they want to investigate. The program will send back some basic information such as volatility and beta value respect to SPY as market.
\
\
**Deployment**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If a user wants to run this code on their own computer without publishing it for others to use, they will need to clone the code from our git and run it on their own desktop via the terminal. Once it is connected, a unique IP address will pop up, which can be copied and pasted into a browser. This will lead to the website, where the user can input data elements such as spot price, strike price, time to maturity, and risk-free rate. If the user wants to run this code and make it publicly available, then they will require an AWS instance or a similar service. 

1.the home page: is the main page when launch the python program. User can either input option information and turn to its result page, or click the 'Manage your portfolio' button at the bottom of the page to explore the portfolio related functionality.
2.the result page: is the page to show results and corresponding models/settings provided by the financial calculator.  
3.the portfolio page: when stitching to this page for the first time, user would type in some stock symbols to create a portfolio. Then there will be textarea that allow user to add new tickers or to remove existing ones. The program will send back basic information of these tickers. Also user could type in the weights of each assets to see the total expected return.
4.At the end of both result page and the portfolio page there is a 'back' button that allow user to go back to the previous page.
\
\
**Next Steps**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Running a comparison on performance times for our function yielded a significant difference depending on where the data was pulled from. For example, we found that pricing an option for a single stock took ~0.5 seconds, and pricing an option for every stock in the Down Jones index using 'yfinance' package took ~10 seconds. This is unacceptable for a project that is designed to scale. By contrast, pricing a single stock using imported data from a csv file took .11 seconds, while pricing an option for the Dow Jones industry stocks with took .15 seconds. Therefore, we believe that the latter source has significant potential for scalling the project and increasing the number of options this website can price quickly if the data is stored, and not called via packages. A difference of several seconds can mean everything for the anticipated end users, as market traders value speed and quick execution when chasing rallies or selling fades. We believe that faster performance times can be one of the most marketable selling points for this product.

Also the portfolio management part still has a lot of room for improvement, for example on generalization and error detect aera.
\
\
