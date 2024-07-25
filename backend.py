import requests
import pandas as pd
import numpy as np #library for numerical operations in Python
import ftplib
from arch import arch_model #GARCH model

ftp_server = ftplib.FTP("ftp.nasdaqtrader.com") #to connect to the ftp of the nasdaqtrader.com and obtain data
ftp_server.login()
ftp_server.encoding = "utf-8"

filenames = ["nasdaqlisted.txt", "otherlisted.txt"] #providing files to read data from

ftp_server.cwd("Symboldirectory") #change working directory to the symbol directory to get the symbols
ftp_server.dir()

for filename in filenames:
    with open(filename, "wb") as file:
        ftp_server.retrbinary(f"RETR {filename}", file.write) #writing binary data of symbols to the file

ftp_server.quit()

# Read Nasdaq listed symbols file into a DataFrame
nasdaq_file = "nasdaqlisted.txt"
nasdaq_df = pd.read_csv(nasdaq_file, delimiter="|")

# Read Other listed symbols file into a DataFrame
other_file = "otherlisted.txt"
other_df = pd.read_csv(other_file, delimiter="|")

# Extract symbols from the dataframes
nasdaq_symbols = nasdaq_df["Symbol"].tolist()
other_symbols = other_df["ACT Symbol"].tolist()  
stock_symbols = pd.concat([nasdaq_symbols, other_symbols], ignore_index=True)

API_KEY = "PJXZ8C7APWZ5VBLO"
Base_url = 'https://www.alphavantage.co/query?'

#SPECIFYING START AND END DATE SO THAT OUR DATA IS ALIGNED AND FOR EASE OF TRAINING MODEL IN CONSTRUCTING OUR DATASET.
start_date = '2024-02-29' #justified as Alpha Vantage API only returns OHLCV data up till 2024-02-29(personally tried and tested)
url = f'{Base_url}function=TIME_SERIES_DAILY&symbol=AAPL&apikey={API_KEY}' #use random ticker in order to constantly update end date to be latest date 
response = requests.get(url)
data = response.json()
end_date = data['Meta Data']['3. Last Refreshed']

# Function to fetch data like OHLCV for a single stock symbol, before using looping to apply function iteratively to all the symbols and obtain all the data to pass into dataframe for model training
def fetch_OHLCV_data(symbol):
    url = f'{Base_url}function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}' # study api endpoints/parameters to figure out how to obtain different data using different commands
    response = requests.get(url)
    data = response.json()
    time_series = data["Time Series (Daily)"]
    
    df = pd.DataFrame.from_dict(time_series, orient='index') #as time_series is in JSON format(key-value), convert it to dataframe from dictionary
    df.index = pd.to_datetime(df.index) #change it to datetime format easier for manipulation eg filtering etc
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.apply(pd.to_numeric) #needed because data in json format is in string form

    filtered_df = df[(df.index >= start_date) & (df.index <= end_date)].copy()
    #This filters the DataFrame to include only the rows where the index (the dates) is within the specified start_date and end_date.
#.copy(): This creates a copy of the filtered DataFrame. 
#Using .copy() ensures that the original DataFrame remains unchanged and prevents potential SettingWithCopyWarning errors.

    return filtered_df

def fetch_ema(symbol):
    url = f'{Base_url}function=EMA&symbol={symbol}&interval=daily&time_period=200&apikey={API_KEY}' # study api endpoints/parameters to figure out how to obtain different data using different commands
    response = requests.get(url)
    data = response.json()
    ema_data = data["Technical Analysis: EMA"] #returns last 200 days of EMA data of that particular stock, if u wish to access a particular stock's EMA, need to index into the value

    df = pd.DataFrame.from_dict(ema_data, orient='index')
    df.index = pd.to_datetime(df.index)
    df.columns = ['EMA']
    df = df.apply(pd.to_numeric)

    filtered_df = df[(df.index >= start_date) & (df.index <= end_date)].copy()
    
    return filtered_df

def fetch_rsi(symbol):
    url = f'{Base_url}function=RSI&symbol={symbol}&interval=daily&time_period=200&series_type=close&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    RSI_data = data['Technical Analysis: RSI']

    df = pd.DataFrame.from_dict(RSI_data, orient='index')
    df.index = pd.to_datetime(df.index)
    df.columns = ['RSI']
    df = df.apply(pd.to_numeric)

    filtered_df = df[(df.index >= start_date) & (df.index <= end_date)].copy()
    
    return filtered_df

#RSI data itself doesnt tell u anything, only gives u the index score whilst 
#check_overbought_oversold gives u the actual desired outcome to interpret buy/sell signals
def check_overbought_oversold(rsi):
    if rsi > 70:
        status = 'Overbought'
    elif rsi < 30:
        status = 'Oversold'
    else:
        status = 'Neutral'
    return status

#MACD cannot be fetched directly from Alpha Vantage API, need to use manual calculation as it's premium api
def calculate_MACD(df, short_window=12, long_window=26, signal_window=9): #window= parameter in python is used to represent time series analysis in stocks(eg number of days be it 7 or 30 days etc)
    df['12 day EMA'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df['26 day EMA'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = df['12 day EMA'] - df['26 day EMA']
    df['Signal line'] = df['Close'].ewm(span=signal_window, adjust=False).mean()
    df['MACD Histogram'] = df['MACD'] - df['Signal line'] #see if histogram is above or below zero line, if above it signals positive bullish momentum, if below means negative bearish momentum
    return df['MACD'], df['Signal line'], df['MACD Histogram']

def fetch_recent_bollinger_bands(symbol):
    url = f'{Base_url}function=BBANDS&symbol={symbol}&interval=daily&time_period=200&nbdevup=2&nbdevdn=2&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    bbands_data = data["Technical Analysis: BBANDS"]

    df = pd.DataFrame.from_dict(bbands_data, orient='index')
    df.index = pd.to_datetime(df.index)
    df.columns = ['Bollinger Bands']
    df = df.apply(pd.to_numeric)
    
    filtered_df = df[(df.index >= start_date) & (df.index <= end_date)].copy()
    
    return filtered_df

def fetch_stock_PEratio(symbol):
    url = f'{Base_url}function=OVERVIEW&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data["PERatio"]

def fetch_stock_PBratio(symbol):
    url = f'{Base_url}function=OVERVIEW&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data["PriceToBookRatio"]

def fetch_stock_EPS(symbol):
    url = f'{Base_url}function=OVERVIEW&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data["EPS"]

def fetch_stock_ROE(symbol):
    url = f'{Base_url}function=OVERVIEW&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data["ReturnOnEquityTTM"]

def obtain_stock_DEratio(symbol): #API does not have direct D/E ratio to fetch, need to calculate it using total liabilities/shareholders' equity
    url = f'{Base_url}function=BALANCE_SHEET&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    latest_balance_sheet = data['annualReports'][0]
    total_liabilities = float(latest_balance_sheet['totalLiabilities']) #rmb change to float format when doing calculations as all data in JSON file is ALL IN STRING!
    shareholders_equity = float(latest_balance_sheet["totalShareholderEquity"])
    debt_to_equity_ratio = total_liabilities/shareholders_equity
    return debt_to_equity_ratio

def fundamental_analysis_stock(PE_ratio, PB_ratio, EPS, ROE, DE_ratio):
    invest_threshold = 3
    score = 0

    if PE_ratio < 15:
        score += 1
    if PB_ratio < 1.5:
        score += 1
    if EPS > 0:
        score += 1
    if ROE > 0.15:
        score += 1
    if DE_ratio < 1:
        score += 1
    if score >= invest_threshold:
        print("Buy")
    else:
        print("Sell/Stay away")
    

def technical_indicators(stock_symbols):
    dfs = [] #empty list to store dataframe of data for EACH stock
    #Extracting and reorganizing the data extracted into a dataframe that allows us to directly pass into ML model for training
    for symbol in stock_symbols: 
        stock_data = fetch_OHLCV_data(symbol)
        ema_data = fetch_ema(symbol)
        rsi_value = fetch_rsi(symbol)
        rsi = check_overbought_oversold(rsi_value)
        MACD, MACD_signal, MACD_histogram = calculate_MACD(stock_data)
        bollinger_bands = fetch_recent_bollinger_bands(symbol)
        df = pd.concat([stock_data, ema_data, rsi_value, pd.Series(rsi, name="STATUS:"), MACD, MACD_signal, MACD_histogram, bollinger_bands], axis=1)
        #pd.series used to work with 1D data, label it with name
        df['Symbol'] = symbol
        dfs.append[df]
    
    #concatenate all the dataframes into a single combined dataframe
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df
    
def fundamental_indicators(stock_symbols): #we're creating a classification model to buy, sell or hold
    # Initialize empty lists to store data
    symbol_list = []
    PE_ratio_list = []
    PB_ratio_list = []
    EPS_list = []
    ROE_list = []
    DE_ratio_list = []
    conclusion_list = []
    for symbol in stock_symbols:
        PE_ratio = fetch_stock_PEratio(symbol)
        PB_ratio = fetch_stock_PBratio(symbol)
        EPS = fetch_stock_EPS(symbol)
        ROE = fetch_stock_ROE(symbol)
        DE_ratio = obtain_stock_DEratio(symbol)
        conclusion = fundamental_analysis_stock(PE_ratio, PB_ratio, EPS, ROE, DE_ratio)   
        
        symbol_list.append(symbol)
        PE_ratio_list.append(PE_ratio)
        PB_ratio_list.append(PB_ratio)
        EPS_list.append(EPS)
        ROE_list.append(ROE)
        DE_ratio_list.append(DE_ratio)
        conclusion_list.append(conclusion)

    df = pd.DataFrame({
    'Symbol': symbol_list,
    'PE Ratio': PE_ratio_list,
    'PB Ratio': PB_ratio_list,
    'EPS': EPS_list,
    'ROE': ROE_list,
    'DE Ratio': DE_ratio_list,
    'Conclusion': conclusion_list
    })
    
    return df

def calculate_GARCH_volatility(symbol, p=1, q=1):
    data = fetch_OHLCV_data(symbol)
    data['Returns'] = data['Close'].pct_change().dropna()
    #usually we use closing price to calculate returns!
    garch_model = arch_model(data['Return'] * 100, vol='Garch', p=p, q=q)
    garch_fitted = garch_model.fit(disp="off") #disp means display to avoid displaying unnecessary info
    #When you fit a GARCH model to your data using the arch library, the model estimates the conditional variance of the returns series over time. This is a measure of volatility.
    garch_forecast = garch_fitted.forecast(start=0) #start=0 means to start from index 0, beginning of dataset
    #After fitting the GARCH model, you can use it to forecast future volatility. 
    # ^^ The forecast method of the GARCH model provides the forecasted variance.
    volatility_forecast = np.sqrt(garch_forecast.variance.values[-1, :]) #This indexing selects the forecasted variance for the most recent period (the last row) in the forecast.
    #Since variance is the square of volatility, taking the square root of the forecasted variance gives the forecasted volatility. Volatility is the standard deviation of returns, which is the square root of the variance.
    
    # Create DataFrame for forecasted volatility
    forecast_dates = data.index[-len(volatility_forecast):]
    volatility_df = pd.DataFrame({
        'Date': forecast_dates,
        'Symbol': symbol,
        'GARCH_Volatility': volatility_forecast
    }).reset_index(drop=True)
    
    return volatility_df

def combine_volatility_for_all(stock_symbols):
    all_volatility_dfs = []
    for symbol in stock_symbols:
        volatility_df = calculate_GARCH_volatility(symbol)
        all_volatility_dfs.append(volatility_df)

    combined_volatility_df = pd.concat(all_volatility_dfs, ignore_index=True)
    return combined_volatility_df

#Have a function/variable to set your start and end dates and apply it to ALL FETCH/CALCULATE DATA FUNCTIONS so that our number of timesteps in our time series data
#for all the data we retrieved are consistent throughout(which is v impt in creating windows etc when training the model aso)

def combined_indicators(stock_symbols):
    technical_df = technical_indicators(stock_symbols)
    fundamental_df = fundamental_indicators(stock_symbols)
    volatility_df = combine_volatility_for_all(stock_symbols)
    #Add garch_volatility df into combined_indicators as well to import as one dataset.
    combined_df = pd.merge(technical_df, fundamental_df, volatility_df, on='Symbol') #merge both dataframes based on keyword Symbol, so that they are concatenated by features on the right to each symbol
    #^^if u straightaway concat both tgt, it is like top to bottom and not joined by symbol.
    return combined_df
#combined_df is basically our x already, what we have just done is feature engineering to prep it for training our regressor model,
#giving us our feature vector combined_df.


