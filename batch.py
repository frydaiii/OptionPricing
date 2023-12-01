# this file computing and compare all options in db
import pandas as pd
from back import black_scholes
from back.utils import get_spot, get_r, get_price_and_r
from datetime import timedelta, datetime
import numpy as np
from back.garch.main import GARCH
from back.gaussian.main import GaussianProcess
import warnings
# warnings.filterwarnings("error")
warnings.filterwarnings("ignore")
import tensorflow as tf

options = pd.read_csv('result_options_2019.csv')


# # Black-Scholes ----------------------------------------------------------------
# dict_r = {}
# dict_stock_data = {}
# bs_result = []
# for _, row in options.iterrows():
#   # if row["quotedate"] != '2019-10-02' or row[
#   #     "expiration"] != '2020-03-20' or row["strike"] != 3500.0 or row["type"]!='put':
#   #   continue
#   # if row["quotedate"] == '2019-10-02' and row[
#   #     "expiration"] == '2020-03-20' and row["strike"] == 3500.0 and row["type"]=='put':
#   #   a = 1
#   expire_date = datetime.strptime(row["expiration"], "%Y-%m-%d")
#   current_date = datetime.strptime(row["quotedate"], "%Y-%m-%d")
#   end_date = current_date
#   start_date = end_date - timedelta(days=365 * 10)
#   if row["quotedate"] in dict_r:
#     r = dict_r[row["quotedate"]]
#     stock_data = dict_stock_data[row["quotedate"]]
#   else:
#     stock_data, r = get_price_and_r(start_date, end_date, "^SPX")
#     r = r[-1]
#     dict_r[row["quotedate"]] = r
#     dict_stock_data[row["quotedate"]] = stock_data
#   spot = stock_data["Close"].iloc[-1]
#   log_return = np.log1p(stock_data["Close"].pct_change().dropna().to_numpy())
#   vol = np.std(log_return) * np.sqrt(252)

#   bs_result.append(
#       black_scholes.OptionPricing(row["type"], spot, row["strike"],
#                                   expire_date, current_date, r, vol))

# options["bs"] = bs_result

# GARCH-------------------------------------------------------------------------
dict_garch_model = {}
dict_r = {}
dict_stock_data = {}
garch_result = []
for _, row in options.iterrows():
  #debug
  # if row["quotedate"] != '2019-10-02' or row[
  #     "expiration"] != '2019-10-14' or row["strike"] != 2850.0 or row["type"]!='call':
  #   continue

  expire_date = datetime.strptime(row["expiration"], "%Y-%m-%d")
  current_date = datetime.strptime(row["quotedate"], "%Y-%m-%d")
  end_date = current_date
  start_date = end_date - timedelta(days=365 * 10)
  if row["quotedate"] in dict_r:
    r = dict_r[row["quotedate"]]
    stock_data = dict_stock_data[row["quotedate"]]
  else:
    stock_data, r = get_price_and_r(start_date, end_date, "^SPX")
    r = r[-1]
    dict_r[row["quotedate"]] = r
    dict_stock_data[row["quotedate"]] = stock_data

  if row["quotedate"] in dict_garch_model:
    model = dict_garch_model[row["quotedate"]]
  else:
    model = GARCH()
    model.InitializeData(start_date, end_date, "^SPX")
    model.Optimize()
    dict_garch_model[row["quotedate"]] = model

  H0 = model.Variance(model.params)[-1]
  spot = stock_data["Close"].iloc[-1]

  garch_result.append(
      model.OptionPricing(row["type"], H0, spot, row["strike"], expire_date,
                          current_date, r))

options["garch"] = garch_result

# # GP----------------------------------------------------------------------------
# dict_gp_model = {}
# dict_r = {}
# dict_stock_data = {}
# gp_result = []
# for _, row in options.iterrows():
#   # debug
#   # if row["quotedate"] != '2019-10-02' or row[
#   #     "expiration"] != '2019-10-14' or row["strike"] != 2850.0 or row["type"]!='call':
#   #   continue

#   expire_date = datetime.strptime(row["expiration"], "%Y-%m-%d")
#   current_date = datetime.strptime(row["quotedate"], "%Y-%m-%d")
#   end_date = current_date
#   start_date = end_date - timedelta(days=365 * 10)
#   if row["quotedate"] in dict_r:
#     r = dict_r[row["quotedate"]]
#     stock_data = dict_stock_data[row["quotedate"]]
#   else:
#     stock_data, r = get_price_and_r(start_date, end_date, "^SPX")
#     r = r[-1]
#     dict_r[row["quotedate"]] = r
#     dict_stock_data[row["quotedate"]] = stock_data

#   if row["quotedate"] in dict_gp_model:
#     model = dict_gp_model[row["quotedate"]]
#   else:
#     model = GaussianProcess()
#     model.InitializeData(start_date, end_date, "^SPX")
#     model.Train()
#     dict_gp_model[row["quotedate"]] = model

#   spot = stock_data["Close"].iloc[-1]

#   gp_result.append(
#       model.OptionPricing(row["type"], spot, row["strike"], expire_date,
#                           current_date, r))

# options["gp"] = gp_result

options.to_csv("result_options_2019.csv")
