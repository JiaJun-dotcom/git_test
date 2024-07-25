import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from keras import Sequential
from keras import LSTM, Dense
import ftplib
from backend import combined_indicators

#ur AI model endpoint is to predict next closing price, and thereby let trader decide on trading strategy with buy/sell signals provided, translating to whether to invest or not invest.
#The features(x) are basically all the combined calculated indicators
#The target variable (y) is the closing price shifted by one day (df['Close'].shift(-1)) to predict the next day's closing price.
#ML algorithm would be LSTM(neural network)
#activation function would be ReLU(predict continuous output like stock price)
#Model should be functional given multiple layers of input required

#Defining LSTM, need to shape input in correct format so LSTM can learn patterns correctly in format (samples, timestamp, features)
#For timestamp, just take the maximum number of days u need from your dataset to ensure consistency
#For features, it is basically total number of x(in feature vector)
#For samples, it is basically just total number of samples for the timestamps u want the data to be split to.
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

#max_timestamp we need is 26 for computing of MACD, the rest follows whilst length of dataset is '2024-02-29' to today
def create_windows(data, window_size): #window_size is the number of timestamps needed, data is the 2D array with features etc to pass in to model for training
    features = []
    labels = []
    for i in range(len(data) - window_size + 1): #eg if len(data)=100, window_size=20days, we would iterate 80 days of data and leave window of 20 days unlooped so that when splitting into training and test dataset later, we can leave one window of data for test dataset.
        features.append(data[i:i + window_size])
        labels.append(data[i:i+window_size]['Close'])
    return np.array(features), np.array(labels)
#For LSTM, we need to define windows of sample data to let LSTM learn about the underlying patterns in long and short term and temporal dependencies of the data etc eg
#Model Training Process
#Create Windows: Use the create_windows function to generate overlapping windows of data.
#Prepare Input and Target Data:
#The input data (X) consists of all the windows except the last value in each window.
#The target data (y) consists of the next value after each window (e.g., the closing price on the next day).
#total number of windows is thus like (len(data)-window_size)+1 eg dataset = 30 days of data, window_size set to be 26, number of windows would be 5, with each window predicting closing price for upcoming day and for LSTM to learn this temporal pattern!
#Train the Model: Use the windows as input samples for training the model.
#^^Just to prepare your time series data in sequential format which models like LSTMs need to understand temporal patterns.
#After the above of separating your data into windows of data, you can then use train_test split to split your data into training and testing datasets to train your model and evaluate its performance

#To differentiate the rows of array of data in the all_features and all_labels array into sets of data corresponding to EACH SYMBOL for their set of timestamps of data for the LSTM to learn BY STOCK SYMBOL
#we use one-hot encoding to convert the categorical variables(stock symbol) to 0 or 1 for LSTM to work with it
def prepare_data_with_embeddings(data, window_size, stock_symbols): 
#we need to segregate the stock symbols into symbol by symbol window data, 
#instead of directly creating windows using the combined_df which would have same symbols row by row and make it very confusing
    encoder = OneHotEncoder(sparse=False) 
#OneHotEncoder(sparse=False): Initializes an instance of OneHotEncoder from scikit-learn.
#sparse=False: By setting sparse=False, the output will be a dense numpy array rather than a sparse matrix.
#A dense array is a standard 2D numpy array with all elements explicitly stored.
    all_features = []
    all_labels = []

    for symbol in stock_symbols:
        symbol_df = data[data['Symbol'] == symbol].drop(columns=['Symbol']) 
#For each symbol:
#Filter Rows: Extract the rows corresponding to that symbol from the combined dataframe using combined_df[combined_df['Symbol'] == symbol].
        X, y = create_windows(symbol_df, window_size) #windows of data are created of eg 26 days per window of all features data in the 26 days and the closing price data in the 26 days
        # Get the one-hot encoding for the current symbol
        symbol_embedding = encoder.transform(np.array([[symbol]])) #a method to transform the array of stock symbols into one-hot encoded format.
        # Repeat the symbol embedding to match the number of windows
        repeated_embedding = np.repeat(symbol_embedding, len(X), axis=0)
        # Expand dimensions to match the shape of X because this allows compiler to know one additional dimension
        #the time dimension has been added to account for the timesteps of data in each window eg 26 days of time series data, needing embedding to know all belongs to this symbol
        repeated_embedding = np.expand_dims(repeated_embedding, axis=1)
        #axis=1 just means adding the new dimension is for ONE TIMESTEP of data
        
        #^^ thus need repeat embedding for window_size for all timesteps of data
        # Repeat the embedding for each time step in the window
        repeated_embedding = np.repeat(repeated_embedding, window_size, axis=1)
        
        # Combine the time series data with the symbol embeddings
        X_with_embedding = np.concatenate([X, repeated_embedding], axis=2)
        #Concatenating along axis=2 combines the features and embeddings, resulting in a shape of (number_of_windows, window_size, number_of_features + embedding_size).
#For example, if number_of_features is 10 and embedding_size is 3, the shape would be (100, 26, 13).
        
        all_features.append(X_with_embedding) #appending all the features to all_features for the 26 days timestep and total number of windows to create depends on length of dataset(200)
        all_labels.append(y)#appending all the labels to all_labels list
#X_with_embedding all these just displays the (shape, window_size, axis) etc instead of outputting the real data inside because all the real data is too much to output BUT 
#rest assured compiler knows the data inside and would still use them to compute, just for ease of representation only shape etc of the entire dataset is shown

    all_features = np.concatenate(all_features, axis=0) #to concatenate the list of arrays in all_features and all_labels into one single array such that each row corresponds to all_features and all_labels for a particular timestep for a particular stock symbol
    all_labels = np.concatenate(all_labels, axis=0)

    return all_features, all_labels


dataframe = combined_indicators(stock_symbols)
input_data = prepare_data_with_embeddings(dataframe, 26, stock_symbols)



