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


def price(options):
  return (options["bid"] + options["ask"]) / 2


def bid_ask(options):
  return 100 * (options["ask"] - options["bid"]) / price(options)


def print_info(options):
  print("price: {:.2f} {:.2f}".format(np.mean(price(options)), np.std(price(options))))
  print("bid ask%: {:.2f} {:.2f}".format(np.mean(bid_ask(options)), np.std(bid_ask(options))))
  print("observations: ", len(options))


options = pd.read_csv('result_options_2019.csv')
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

print_info(deep_itm_call)

# bs_result = options["bs"].to_numpy()
# garch_result = options["garch"].to_numpy()
# gp_result = options["gp"].to_numpy()
# market_result = (options["bid"].to_numpy() + options["ask"].to_numpy()) / 2

# bs_rmse = calculate_rmse(bs_result, market_result)
# garch_rmse = calculate_rmse(garch_result, market_result)
# gp_rmse = calculate_rmse(gp_result, market_result)

# print("Black-Scholes: ", bs_rmse)
# print("GARCH: ", garch_rmse)
# print("Gaussian Process: ", gp_rmse)
