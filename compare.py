import pandas as pd
import numpy as np

def calculate_rmse(a, b):
    # Ensure both arrays have the same shape
    assert a.shape == b.shape, "Arrays must have the same shape"

    # Calculate the squared differences
    squared_diff = (a - b) ** 2

    # Calculate the mean squared difference
    mean_squared_diff = np.mean(squared_diff)

    # Calculate the square root of the mean squared difference
    rmse = np.sqrt(mean_squared_diff)

    return rmse

options = pd.read_csv('result_options_2019.csv')
options_2 = pd.read_csv('options_2019_2.csv')
options["underlying_last"] = options_2["underlying_last"]
options = options[options["strike"]/options["underlying_last"] > 1.15]

bs_result = options["bs"].to_numpy()
garch_result = options["garch"].to_numpy()
gp_result = options["gp"].to_numpy()
market_result = (options["bid"].to_numpy() + options["ask"].to_numpy()) / 2

bs_rmse = calculate_rmse(bs_result, market_result)
garch_rmse = calculate_rmse(garch_result, market_result)
gp_rmse = calculate_rmse(gp_result, market_result)

print("Black-Scholes: ", bs_rmse)
print("GARCH: ", garch_rmse)
print("Gaussian Process: ", gp_rmse)