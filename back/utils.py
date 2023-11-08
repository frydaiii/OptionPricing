from datetime import timedelta, datetime
import yfinance as yf
import numpy as np
import math
import pandas as pd
import string
import random

def get_data(start_date, end_date, ticker="^SPX"):
    # if type(start_date) is str:
    #     start_date = datetime.strptime(start_date, "%Y-%m-%d")
    # if type(end_date) is str:
    #     end_date = datetime.strptime(end_date, "%Y-%m-%d")
    start_date = datetime.strftime(start_date, "%Y-%m-%d")
    end_date = datetime.strftime(end_date, "%Y-%m-%d")
    if ticker != "^SPX":
        return yf.download(ticker, start=start_date, end=end_date)
    
    file_path = "spx_historical_data_2008_2020.csv"

    # Read the CSV file into a DataFrame
    historical_data = pd.read_csv(file_path)

    # Convert the 'Date' column to a datetime object
    historical_data['Date'] = pd.to_datetime(historical_data['Date'], utc=True)

    # Filter the data based on the date range
    filtered_data = historical_data[(historical_data['Date'] >= start_date) & (historical_data['Date'] <= end_date)]

    return filtered_data

def get_r(end_date):
    # get risk free rate, is us treasury bonds in 3 months
    if type(end_date) is str:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    tb_rate = yf.download("^IRX", start=end_date - timedelta(days=3), end=end_date)
    r = tb_rate.iloc[-1]["Close"] or tb_rate.iloc[0]
    return r / 100


def get_volatility_ticker(ticker, date):
    if type(date) is str:
        date = datetime.strptime(date, "%Y-%m-%d")
    # filter
    if ticker == "SPX":
        ticker = "^SPX"
    # create train data is data 10 years before current_date
    end_date = date
    start_date = end_date - timedelta(days=365 * 10)

    stock_data = {}
    if ticker == "^SPX":
        stock_data = get_data(start_date, end_date)
    else:
        stock_data = yf.download(ticker, start=start_date, end=end_date)

    df_close = stock_data["Close"]
    train_data = df_close
    dSprice = np.diff(train_data.to_numpy())
    Sprice = train_data.to_numpy()[:-1]
    volatility = math.sqrt(np.mean(dSprice * dSprice / (Sprice * Sprice * 1 / 365)))
    return volatility


def get_volatility(date):
    return get_volatility_ticker("SPX", date)


def get_spot_ticker(ticker, date):
    if type(date) is str:
        date = datetime.strptime(date, "%Y-%m-%d")
    if ticker == "SPX":
        ticker = "^SPX"
    end_date = date
    start_date = end_date - timedelta(days=5)

    stock_data = get_data(start_date, end_date, ticker)
    # if ticker == "^SPX":
    #     stock_data = get_data(start_date, end_date)
    # else:
    #     stock_data = yf.download(ticker, start=start_date, end=end_date)

    df_close = stock_data["Close"]
    return df_close.iloc[-1]


def get_spot(date):
    return get_spot_ticker("SPX", date)

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def get_close_price_r(start_date, end_date, ticker):
    stock_data = get_data(start_date, end_date, ticker)
    df_close = stock_data["Close"]
    r = get_r(end_date)
    return (df_close, r)