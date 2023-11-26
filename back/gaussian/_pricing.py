import tensorflow as tf
from datetime import datetime
import numpy as np
from typing import List
from back.utils import get_spot_ticker, get_r, dte_count


class PricingMixin(object):

  def OptionPricing(self, type: str, spot: float, strike_price: float,
                    expire_date: datetime, current_date: datetime, r: float):
    assert current_date == self.end_date
    dte = dte_count(current_date, expire_date)
    sims = 10000
    X_star = tf.range(self.N, self.N + dte, dtype=tf.float64)
    X_star = tf.expand_dims(X_star, axis=1)
    f = self.model.predict_f_samples(X_star, sims).numpy().squeeze().T
    # predicted_Y_mean, predicted_Y_var = self.model.predict_y(X_star)
    z = np.random.normal(size=[dte, sims])
    softplus_f = np.log(1 + np.exp(f))
    Y = softplus_f + 2 * np.sqrt(softplus_f) * z

    spot = tf.cast(spot, tf.float64)
    K = tf.cast(strike_price, tf.float64)
    daily_r = tf.cast(r / 360, tf.float64)

    # random = tf.random.normal(shape=[dte, sims],
    #                           mean=0.0,
    #                           stddev=1.0,
    #                           dtype=tf.float64)
    log_return = daily_r - tf.cast(0.5, tf.float64) * Y
    ln_S = tf.math.log(spot) + tf.math.cumsum(log_return, axis=0)

    S = tf.math.exp(ln_S)
    if type == "call":
      payoffs = np.maximum(S - K, 0)
    else:
      payoffs = np.maximum(K - S, 0)

    option_price = np.mean(payoffs) * np.exp(-r * (dte / 365))
    return option_price

  def OptionsPricing(self, type: str, strike_prices: List[float],
                     expire_dates: List[datetime],
                     current_date: datetime) -> List[float]:
    assert not (len(strike_prices) > 1 and len(expire_dates) > 1)
    assert current_date == self.end_date
    spot = get_spot_ticker(self.ticker, current_date)
    r = get_r(current_date)
    prices = []
    for strike_price in strike_prices:
      for expire_date in expire_dates:
        prices.append(
            self.OptionPricing(type, spot, strike_price, expire_date,
                               current_date, r))
        self.task.update_state(state="CALCULATING",
                               meta={
                                   "current": len(prices),
                                   "total":
                                   len(strike_prices) * len(expire_dates)
                               })

    return prices
