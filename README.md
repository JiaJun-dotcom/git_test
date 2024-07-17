# git_test
This is a stock analyzer on real-time stock data, focused on TECHNICAL ANALYSIS OF THE US STOCK MARKET
-Connected to Alpha Vantage API on intraday time-series stock data
-Obtain the tickers(all stock symbols available on US market) using FTP(File transfer protocol)-- used Filezilla to connect to the directory.

Its Alpha intelligence API to analyse recent news and sentiments that can affect buying of stock

Its Analytics API as well which has endpoints that returns a rich set of advanced analytics metrics

We would take the most important metrics determining whether to buy/sell a stock of price metrics:
-Price metrics eg Volume of stock traded for that period, open, high, low and closing stock prices(basically main data we need to retrieve from the API in json format)

- Exponential moving averages(Average of a selected range of prices, typically closing prices, over a specified number of periods, giving more weight through exponentiation to more recent prices.)

- Relative Strength Index (RSI) that measures the speed and change of price movements(RSI values above 70 typically indicate overbought conditions, and below 30 indicate oversold conditions)


Obtained data from API then we can build into a pandas dataframe for use to train our ML prediction model for predicting whether or not to invest in the stock(formulate the hypothesis, represent the outcome as either O or 1)


