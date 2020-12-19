
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
We wanted to apply some of the skills we have learned in this class towards created fast and user-friendly financial tools. One of the main benefits of this project is that it has a lot of built-in user flexibility that allows for detailed results with a faster turnaround time than any simple solver-driven excel sheet can provide. Importantly, this project represents a baseline that is very scalable if the data is stored in a database, as opposed to downloading the necessary historical data from a package with every user request. Observing the differences in runtime helped in forming this conclusion and developing a product that is much more scalable.
\
\
**List of features for usage**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
1. Data visualization tools, including daily historical returns in a line plot and weekly historical returns in a candlestick chart.
2. Detailed model feature selection, including model type, maturity type, and option type.
3. User-friendly input of spot price, strike price, time to maturity, and risk-free rate.
4. Automatically calculates historical vol given start/end dates for adjusted closing prices of the underlying asset.
5. Run-time feature with direct comparison of pricing single-stock option using 'yfinance' package versus importing the data via a csv file, as well as pricing stock options for all 30 stocks in DJIA from 'yfinance' package versus imported csv files.
\
\
**Deployment**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If a user wants to run this code on their own computer without publishing it for others to use, they will need to clone the code from our git and run it on their own desktop via the terminal. Once it is connected, a unique IP address will pop up, which can be copied and pasted into a browser. This will lead to the website, where the user can input data elements such as spot price, strike price, time to maturity, and risk-free rate. If the user wants to run this code and make it publicly available, then they will require an AWS instance or a similar service. 
\
\
**Next Steps**
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Running a comparison on performance times for our function yielded a significant difference depending on where the data was pulled from. For example, we found that pricing an option for a single stock took ~0.5 seconds, and pricing an option for every stock in the Down Jones index using 'yfinance' package took ~10 seconds. This is unacceptable for a project that is designed to scale. By contrast, pricing a single stock using imported data from a csv file took .11 seconds, while pricing an option for the Dow Jones industry stocks with took .15 seconds. Therefore, we believe that the latter source has significant potential for scalling the project and increasing the number of options this website can price quickly if the data is stored, and not called via packages. A difference of several seconds can mean everything for the anticipated end users, as market traders value speed and quick execution when chasing rallies or selling fades. We believe that faster performance times can be one of the most marketable selling points for this product.
\
\
