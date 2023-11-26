# this file computing and compare all options in db
import pandas as pd
from back import black_scholes
from back.utils import get_spot, get_r, get_price_and_r
from datetime import timedelta, datetime
import numpy as np
from back.garch.main import GARCH
from back.gaussian.main import GaussianProcess
import warnings
warnings.filterwarnings("error")

options = pd.read_csv('options_2019.csv')

dict_r = {}

# Black-Scholes ----------------------------------------------------------------
bs_result = []
for _, row in options.iterrows():
  expire_date = datetime.strptime(row["expiration"], "%Y-%m-%d")
  current_date = datetime.strptime(row["quotedate"], "%Y-%m-%d")
  end_date = current_date
  start_date = end_date - timedelta(days=365 * 10)
  if row["quotedate"] in dict_r:
    r = dict_r[row["quotedate"]]
  else:
    stock_data, r = get_price_and_r(start_date, end_date, "^SPX")
    r = r[-1]
    dict_r[row["quotedate"]] = r
  spot = stock_data["Close"].iloc[-1]
  log_return = np.log1p(stock_data["Close"].pct_change().dropna().to_numpy())
  vol = np.std(log_return) * np.sqrt(252)

  bs_result.append(
      black_scholes.OptionPricing(row["type"], spot, row["strike"],
                                  expire_date, current_date, r, vol))

options["bs"] = bs_result

# GARCH-------------------------------------------------------------------------
dict_garch_model = {}
garch_result = []
for _, row in options.iterrows():
  #debug
  # if row["quotedate"] != '2019-11-06' or row[
  #     "expiration"] != '2019-11-18':
  #   continue

  expire_date = datetime.strptime(row["expiration"], "%Y-%m-%d")
  current_date = datetime.strptime(row["quotedate"], "%Y-%m-%d")
  end_date = current_date
  start_date = end_date - timedelta(days=365 * 10)
  if row["quotedate"] in dict_r:
    r = dict_r[row["quotedate"]]
  else:
    stock_data, r = get_price_and_r(start_date, end_date, "^SPX")
    r = r[-1]
    dict_r[row["quotedate"]] = r

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

# GP----------------------------------------------------------------------------
dict_gp_model = {}
gp_result = []
for _, row in options.iterrows():
  # debug
  if row["quotedate"] != '2019-10-02' or row[
      "expiration"] != '2019-10-18' or row["strike"] != 3030.0:
    continue

  expire_date = datetime.strptime(row["expiration"], "%Y-%m-%d")
  current_date = datetime.strptime(row["quotedate"], "%Y-%m-%d")
  end_date = current_date
  start_date = end_date - timedelta(days=365 * 10)
  if row["quotedate"] in dict_r:
    r = dict_r[row["quotedate"]]
  else:
    stock_data, r = get_price_and_r(start_date, end_date, "^SPX")
    r = r[-1]
    dict_r[row["quotedate"]] = r

  if row["quotedate"] in dict_gp_model:
    model = dict_gp_model[row["quotedate"]]
  else:
    model = GaussianProcess()
    model.InitializeData(start_date, end_date, "^SPX")
    model.Train()
    dict_gp_model[row["quotedate"]] = model

  spot = stock_data["Close"].iloc[-1]

  gp_result.append(
      model.OptionPricing(row["type"], spot, row["strike"], expire_date,
                          current_date, r))

options["gp"] = gp_result

options.to_csv("result_options_2019.csv")
