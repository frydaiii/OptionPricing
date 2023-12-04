from datetime import timedelta, datetime
import yfinance as yf
import numpy as np
import math
import pandas as pd
import string
import random


# _todo convert name to snakecase
def get_data(start_date: datetime,
             end_date: datetime,
             ticker: str = "^SPX") -> pd.DataFrame:
  if ticker != "^SPX":
    return yf.download(ticker, start=start_date, end=end_date)

  file_path = "spx_historical_data_2008_2020.csv"

  # Read the CSV file into a DataFrame
  historical_data = pd.read_csv(file_path)

  # Convert the 'Date' column to a datetime object
  historical_data['Date'] = pd.to_datetime(historical_data['Date'],
                                           utc=True).dt.date

  # Filter the data based on the date range
  filtered_data = historical_data[
      (historical_data['Date'] >= start_date.date())
      & (historical_data['Date'] <= end_date.date())]

  return filtered_data


def get_r(end_date: datetime) -> float:
  # get risk free rate, is us treasury bonds in 3 months
  if type(end_date) is str:
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
  tb_rate = yf.download("^IRX",
                        start=end_date - timedelta(days=3),
                        end=end_date)
  r = tb_rate.iloc[-1]["Close"] or tb_rate.iloc[0]
  return r / 100


def get_volatility_ticker(ticker: str, date: datetime) -> float:
  if ticker == "SPX" or ticker == "SPXW":
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
  volatility = math.sqrt(
      np.mean(dSprice * dSprice / (Sprice * Sprice * 1 / 365)))
  return volatility


def get_volatility(date: datetime) -> float:
  return get_volatility_ticker("SPX", date)


def get_spot_ticker(ticker: str, date: datetime) -> float:
  if type(date) is str:
    date = datetime.strptime(date, "%Y-%m-%d")
  if ticker == "SPX" or ticker == "SPXW":
    ticker = "^SPX"
  end_date = date
  start_date = end_date - timedelta(days=5)

  stock_data = get_data(start_date, end_date, ticker)

  df_close = stock_data["Close"]
  return df_close.iloc[-1]


def get_spot(date: datetime) -> float:
  return get_spot_ticker("SPX", date)


def get_price_and_r(start_date: datetime, end_date: datetime,
                    ticker: str) -> (pd.DataFrame, []):
  stock_data = get_data(start_date, end_date, ticker)
  stock_data['Date'] = pd.to_datetime(stock_data['Date'])
  if (start_date > datetime.strptime("1990-01-01", "%Y-%m-%d") and 
      end_date < datetime.strptime("2020-01-01", "%Y-%m-%d")):
    tb_rate = pd.read_csv("tbill.csv")
    tb_rate['time'] = pd.to_datetime(tb_rate['time'])
    filtered_rate = tb_rate[tb_rate['time'].isin(stock_data['Date'])]
    filtered_rate['rate'] = filtered_rate["rate"].replace('ND', None).ffill()
    r = filtered_rate['rate'].to_numpy()[1:]
    r = np.asarray(r, dtype=float) / 100
  else:
    tb_rate = yf.download("^IRX", start=start_date, end=end_date)
    r = tb_rate["Close"].to_numpy()[1:] / 100
  if len(r) < len(stock_data) - 1:
    gap = len(stock_data) - len(r)
    for _ in range(1, gap):
      r = np.append(r, r[-1])

  # if len(r) != len(stock_data):
  #   print("r-----", len(r))
  #   print("stock_data-----", len(stock_data))

  assert len(r) == len(stock_data) - 1
  return (stock_data, r)

def dte_count(start_date, end_date):
    # Calculate the total number of days between start_date and end_date
    total_days = (end_date - start_date).days

    # Calculate the number of weekend days within the total_days range
    weekend_days = 0
    for day in range(total_days + 1):
        current_day = start_date + timedelta(days=day)
        if current_day.weekday() in [5, 6]:  # 5 is Saturday, 6 is Sunday
            weekend_days += 1

    # Calculate the weekday difference by subtracting weekend days
    weekday_difference = total_days - weekend_days

    return weekday_difference
