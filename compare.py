import pandas as pd
import numpy as np


def calculate_rmse(a, b):
  # Ensure both arrays have the same shape
  assert a.shape == b.shape, "Arrays must have the same shape"

  # Calculate the squared differences
  squared_diff = (a - b)**2

  # Calculate the mean squared difference
  mean_squared_diff = np.mean(squared_diff)

  # Calculate the square root of the mean squared difference
  rmse = np.sqrt(mean_squared_diff)

  return rmse

def calculate_mae(a, b):
    # Ensure both arrays have the same shape
    assert a.shape == b.shape, "Arrays must have the same shape"

    # Calculate the absolute differences
    absolute_diff = np.abs(a - b)

    # Calculate the mean absolute difference
    mean_absolute_diff = np.mean(absolute_diff)

    return mean_absolute_diff

def calculate_mdape(a, b):
    # Ensure both arrays have the same shape
    assert a.shape == b.shape, "Arrays must have the same shape"

    # Calculate absolute percentage errors
    absolute_percentage_error = np.abs((a - b) / b) * 100

    # Calculate the median absolute percentage error
    mdape = np.median(absolute_percentage_error)

    return mdape

def price(options):
  return (options["bid"] + options["ask"]) / 2


def bid_ask(options):
  return 100 * (options["ask"] - options["bid"]) / price(options)


def print_info(options):
  print("price: {:.2f} {:.2f}".format(np.mean(price(options)), np.std(price(options))))
  print("bid ask%: {:.2f} {:.2f}".format(np.mean(bid_ask(options)), np.std(bid_ask(options))))
  print("observations: ", len(options))


options = pd.read_csv('result_options_2019_10.csv')
options_2 = pd.read_csv('options_2019_2.csv')
options["underlying_last"] = options_2["underlying_last"]
options["expiration"] = pd.to_datetime(options["expiration"])
options["quotedate"] = pd.to_datetime(options["quotedate"])

# deep_otm_put = options[
#     (options["type"] == "put")
#     & (options["strike"] / options["underlying_last"] < 0.85) &
#     ((options["expiration"] - options["quotedate"]).dt.days < 60)]
# deep_otm_put = options[
#     (options["type"] == "put")
#     # & (options["strike"] / options["underlying_last"] >= 1)
#     & (options["strike"] / options["underlying_last"] > 1.15)
#     # & ((options["expiration"] - options["quotedate"]).dt.days >= 60)
#     & ((options["expiration"] - options["quotedate"]).dt.days > 160)
#     ]

# print_info(deep_otm_put)
deep_itm_call = options[
    (options["type"] == "call")
    & (options["strike"] / options["underlying_last"] > 1.15)
    # & (options["strike"] / options["underlying_last"] >= 1)
    # & ((options["expiration"] - options["quotedate"]).dt.days >= 60)
    & ((options["expiration"] - options["quotedate"]).dt.days > 160)
    ]

# print_info(deep_itm_call)

def print_result(options):
  bs_result = options["bs"].to_numpy()
  garch_result = options["garch"].to_numpy()
  gp_result = options["gp"].to_numpy()
  market_result = (options["bid"].to_numpy() + options["ask"].to_numpy()) / 2

  bs_rmse = calculate_rmse(bs_result, market_result)
  garch_rmse = calculate_rmse(garch_result, market_result)
  gp_rmse = calculate_rmse(gp_result, market_result)

  bs_mae = calculate_mae(bs_result, market_result)
  garch_mae = calculate_mae(garch_result, market_result)
  gp_mae = calculate_mae(gp_result, market_result)

  bs_mdape = calculate_mdape(bs_result, market_result)
  garch_mdape = calculate_mdape(garch_result, market_result)
  gp_mdape = calculate_mdape(gp_result, market_result)

  print("RMSE Black-Scholes: {:.2f}".format(bs_rmse))
  print("RMSE GARCH: {:.2f}".format(garch_rmse))
  print("RMSE Gaussian Process: {:.2f}\n--------------------------".format(gp_rmse))

  print("MAE Black-Scholes: {:.2f}".format(bs_mae))
  print("MAE GARCH: {:.2f}".format(garch_mae))
  print("MAE Gaussian Process: {:.2f}\n--------------------------".format(gp_mae))

  print("MdAPE Black-Scholes: {:.2f}".format(bs_mdape))
  print("MdAPE GARCH: {:.2f}".format(garch_mdape))
  print("MdAPE Gaussian Process: {:.2f}".format(gp_mdape))

  # print("Min Black-Scholes: {:.2f}".format(np.min(bs_result-market_result)))
  # print("Min GARCH: {:.2f}".format(np.min(garch_result-market_result)))
  # print("Min Gaussian Process: {:.2f}".format(np.min(gp_result-market_result)))

  # print("Max Black-Scholes: {:.2f}".format(np.max(bs_result-market_result)))
  # print("Max GARCH: {:.2f}".format(np.max(garch_result-market_result)))
  # print("Max Gaussian Process: {:.2f}".format(np.max(gp_result-market_result)))


  # print(options[options["bs"]-(options["bid"].to_numpy() + options["ask"].to_numpy()) / 2==np.min(bs_result-market_result)])

deep_itm_call = options[
    (options["type"] == "put")
    & (options["strike"] / options["underlying_last"] > 1.15)
    # & (options["strike"] / options["underlying_last"] < 1.15)
    # & ((options["expiration"] - options["quotedate"]).dt.days >= 60)
    & ((options["expiration"] - options["quotedate"]).dt.days > 160)
    ]
# print_result(deep_itm_call)

# print(options.loc[32266])


for _, row in options.iterrows():
   if np.abs((row["bs"]-(row["bid"]+row["ask"])/2)/-(row["bid"]+row["ask"])) > 0.5:
      print(row)
      break