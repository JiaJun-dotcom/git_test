# git_test
This is a stock analyzer on stock data to predict upcoming price and trends of specific stocks requested by user, focusing on both FUNDAMENTAL and TECHNICAL ANALYSIS OF THE US STOCK MARKET in NASDAQ and other listed stocks.
-Connected to Alpha Vantage API to extract relevant data.
-Obtained the tickers(all stock symbols available on US market) using FTP(File transfer protocol)-- used Filezilla to connect to the NASDAQ directory.
-For indicators: OHLCV, EMA, RSI, MACD and Bollinger Bands, I had to include start_date and end_date to specify data range for the data and ensure they configure to same format starting from '2024-02-29' as its the earliest OHLCV stock data available when connecting to Alpha Vantage API for all stocks.

Its Alpha intelligence API to analyse recent news and sentiments that can affect buying of stock

Its Analytics API as well which has endpoints that returns a rich set of advanced analytics metrics

TECHNICAL ANALYSIS
We would take the most important metrics determining whether to buy/sell a stock of price metrics:
-Price metrics eg Volume of stock traded for that period, open, high, low and closing stock prices(basically main data we need to retrieve from the API in json format)
^^What we need from API is TIME_SERIES_DAILY data that returns the OHLCV data of EACH symbol in the symbols we obtained from FTP.

- A stock is considered overbought when it has experienced a significant and sustained upward move, suggesting that it may be trading at a price higher than its intrinsic value.
Overbought conditions often indicate that the stock is due for a price correction or pullback. It can be a signal that the buying momentum is overextended and that the stock price might decrease soon.(Thus sellers may choose to sell and take profits when a stock is overbought)

- A stock is considered oversold when it has experienced a significant and sustained downward move, suggesting that it may be trading at a price lower than its intrinsic value. Oversold conditions often indicate that the stock is due for a price increase or rebound. It can be a signal that the selling momentum is overextended and that the stock price might increase soon. (Traders might consider buying when a stock is oversold.)

4 Technical Indicators:
- Exponential moving averages(Average of a selected range of prices, typically closing prices, over a specified number of periods, giving more weight through exponentiation to more recent prices.) **

- Relative Strength Index (RSI) that measures the speed and change of price movements(RSI values above 70 typically indicate overbought conditions, and below 30 indicate oversold conditions, between 30 and 70 indicate neutral conditions) -- Mechanism to check for overbought/oversold conditions.
 The RSI oscillates between 0 and 100 and is typically used with a 14-day time frame.
 Over the specified period (usually 14 days), calculate the average of all gains and losses.
 Relative strength = Average gain/Average loss
 RSI=100−(100/(1+RS))

- MACD(Moving Averages Convergence Divergence) that tells us potential buy and sell signals, if the MACD line(diff between MOST RECENT 12-day and 26-day EMA) has been increasing and crosses the Signal line(most recent 9 day EMA), it suggest that recent price increases are likely to continue just like the MACD line, suggesting buy opportunity whilst if it has been decreasing and crosses below Signal line, suggests that recent price decreases may continue, indicating sell opportunity.
Example Calculation
Calculate the 12-day EMA: Sum the closing prices of the last 12 days, then apply the EMA formula.
Calculate the 26-day EMA: Sum the closing prices of the last 26 days, then apply the EMA formula.
MACD Line: Subtract the 26-day EMA from the 12-day EMA. (MACD LINE)
Signal Line: Calculate the 9-day EMA of the stock. (SIGNAL LINE)
-- Bullish Divergence: When the stock price is making lower lows while the MACD is making higher lows, it suggests a potential reversal to an upward trend.
-- Bearish Divergence: When the stock price is making higher highs while the MACD is making lower highs, it indicates a potential reversal to a downward trend.
^^Basically for our project what we need to have is just the data to plot both lines and plotting the lines possibly, from there then predict buy or sell opportunity/next closing price will increase or decrease.                             

- Bollinger Bands: They are used to measure market volatility and identify potential overbought or oversold conditions. 
Bollinger Bands consist of three lines: the middle band (a 20-day simple moving average), and the upper and lower bands (which are 2 standard deviations above and below the middle band respectively).
Calculation:
-- Middle Band (SMA): Calculate the 20-day SMA of the stock's closing prices.
-- Standard Deviation: Calculate the standard deviation of the same 20-day period.
-- Upper Band: Middle Band + (2 * Standard Deviation)
-- Lower Band: Middle Band - (2 * Standard Deviation)
Prices tend to bounce within the bands, returning to the middlenear the upper band. (Bollinger Bounce)
(At upper band signals overbought condition, price likely to drop and return back to middle band, at lower band signals oversold condition, price likely to rise back to middle band)
When the bands are very close together, it indicates low volatility and potential for a breakout.(Bollinger squeeze) A squeeze often precedes a significant price movement, whereby traders predict price according to direction of the breakout(when price moves outside of the band)

FUNDAMENTAL ANALYSIS
Financial data of the stock and company eg P/E ratio, revenues, debts etc

-Key understanding is that Overvalued means company's share price is overvalued relative to its fundamentals(revenue, profits, p/e ratio wtv), which can be interpreted as a signal that stock prices may fall in future and indicates sell opportunity, whilst undervalued means vice versa and indicates buy opportunity.

Key financial metrics required:
P/E Ratio(The P/E ratio measures a company's current share price relative to its earnings per share (EPS). It indicates how much investors are willing to pay per dollar of earnings, helping to assess whether a stock is overvalued or undervalued compared to its earnings.)
- P/E Ratio= Earnings per Share (EPS) / Market Value per Share
​
P/B Ratio(The P/B ratio compares a company's market value to its book value (net asset value).It shows the value that market participants attach to a company's equity relative to the book value of its equity. A low P/B ratio might indicate an undervalued stock.)
- P/B Ratio = Market Value per Share / Book Value per Share
​
Earnings Per Share (EPS) (EPS represents the portion of a company's profit allocated to each outstanding share of common stock. It is a key indicator of a company's profitability and is often used as a metric to gauge financial performance over time.)
- EPS = (Net Income−Dividends on Preferred Stock) / Average Outstanding shares
​
Return on Equity (ROE) (ROE measures a corporation's profitability by revealing how much profit a company generates with the money shareholders have invested. It indicates how efficiently a company is using its equity to generate profit. Higher ROE values generally indicate a more efficient company in terms of profit generation.)
- ROE = Net Income / Shareholders Equity

Debt-to-Equity (D/E) Ratio (It provides insight into a company's financial leverage and risk. A high D/E ratio may indicate that a company is heavily reliant on debt to finance its growth, which could be risky if not managed properly.)
- D/E Ratio = Total Liabilities / Shareholders' Equity

^^ Can be reliable financial indicators of company position now and we obtain them by using Alpha vantage's API of fetching company overview.(FUNCTION=OVERVIEW when querying the API)

--For fundamentals analysis, we can generalize them using a particular fundamental score to judge whether or not to invest in the stock(eg for high EPS, low D/E ratio etc, give it a credit score of 1 for each, else give it a credit score of 0 and define thresholds for each metric value, based off that 
score determine whether to invest or not, total /5, if >= 3, can invest.)
FAVOURABLE THRESHOLDS(score += 1):
P/E ratio < 15
P/B ratio < 1.5
EPS：Positive
D/E < 1
ROE > 15%
^^SHORTCOMINGS:
- Different industry can have different thresholds for each metric, may not be accurate
- Certain factors may be more significant in affecting the decision to invest than others.
- Current market dynamics can constantly change, and so can thresholds, thus take with a pinch of salt.

For news sentiments, just set function = NEWS_SENTIMENT, there is a sentiment score in the api and from that we can judge bullish/bearish performance of the stock.

Obtained data from API then we can build into a pandas dataframe for use to train our ML regressor model for predicting whether or not to invest in the stock based on buy/sell signals (formulate the hypothesis, represent the outcome as either O or 1)
By using historical data, the regression model learns the relationship between fundamental and technical metrics and stock prices. This relationship is then used to predict future prices based on the current values of these metrics. 
Use performance metrics like RMSE (Root Mean Squared Error), MAE (Mean Absolute Error), or MSE (Mean Squared Error) to assess the accuracy of your predictions.
^^TO BUILD INTO A SINGLE DATAFRAME, use pd.concat([master_df, stock_data], axis=1)

-Flask is to interact with Python backend, allows you to create web applications and serve HTML pages, interact with a Python backend, and handle HTTP requests and responses through a web server. Flask makes it easy to connect your Python code to a web interface, enabling you to build dynamic web applications.

Need to create an app route with Flask first to link to your stock end point with a GET method to retrieve stock data for that symbol when defining the function fetchstockdata in scripts.js to
have eg from url: "\analyze?queryparameters..."
Connecting to Flask allows you to create a web server that can serve your HTML interface and handle requests to perform operations such as analyzing stock data, predicting closing prices, and interacting with your AI model.





