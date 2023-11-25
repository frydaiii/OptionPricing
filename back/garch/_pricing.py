import tensorflow as tf
from datetime import datetime
import numpy as np
from typing import List
from back.utils import get_spot_ticker, get_r
from statistics import variance


class PricingMixin(object):

  def OptionPricing(self, type, H0: float, spot: float, strike_price: float,
                    expire_date: datetime, current_date: datetime, r: float):
    omega = self.params[0]
    alpha = self.params[1]
    beta = self.params[2]
    lambd = self.params[3]
    daily_r = r / 365
    dte = (expire_date - current_date).days
    T = dte / 365
    steps = dte
    num_simulations = 1000
    Z = np.random.normal(size=(steps + 1, num_simulations))
    # H0 = variance(self.log_returns)
    H = np.empty(shape=(steps, num_simulations))
    H = np.concatenate((np.full(shape=(1, num_simulations), fill_value=H0), H))
    lnS = np.empty(shape=(steps, num_simulations))
    lnS = np.concatenate((np.full(shape=(1, num_simulations),
                                  fill_value=np.log(spot)), lnS))
    for i in range(1, steps + 1):
      # _todo this formula could be shorten by using cumsum
      H[i] = omega + (alpha * (Z[i - 1] - lambd)**2 + beta) * H[i - 1]
      lnS[i] = lnS[i - 1] + daily_r - 0.5 * H[i] + Z[i] * np.sqrt(H[i])

    paths = np.exp(lnS)
    if type == "call":
      payoffs = np.maximum(paths[-1] - strike_price, 0)
    else:
      payoffs = np.maximum(strike_price - paths[-1], 0)
    option_price = np.mean(payoffs) * np.exp(
        -r * T)  # discounting back to present value
    return option_price

  def OptionsPricing(self, type: str, H0: float, strike_prices: List[float],
                     expire_dates: List[datetime],
                     current_date: datetime) -> List[float]:
    assert not (len(strike_prices) > 1 and len(expire_dates) > 1)
    spot = get_spot_ticker(self.ticker, current_date)
    r = get_r(current_date)
    prices = []
    for strike_price in strike_prices:
      for expire_date in expire_dates:
        prices.append(
            self.OptionPricing(type, H0, spot, strike_price, expire_date,
                               current_date, r))
        self.task.update_state(state="CALCULATING",
                               meta={
                                   "current": len(prices),
                                   "total":
                                   len(strike_prices) * len(expire_dates)
                               })

    return prices
