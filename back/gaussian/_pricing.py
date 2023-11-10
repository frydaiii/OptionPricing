import tensorflow as tf
from datetime import datetime
import numpy as np
from typing import List
from back.utils import get_spot_ticker, get_r

class PricingMixin(object):
  def OptionPricing(self, spot: float, strike_price: float, 
                expire_date: datetime, current_date: datetime, r: float):
    assert current_date == self.end_date
    dte = (expire_date - current_date).days
    X_star = tf.cast(tf.range(self.N, self.N + dte), tf.float64)
    X_star = tf.expand_dims(X_star, axis=1)
    predicted_Y_mean, predicted_Y_var = self.model.predict_y(X_star)

    spot = tf.cast(spot, tf.float64)
    K = tf.cast(strike_price, tf.float64)
    daily_r = tf.cast(r / 360 ,tf.float64)
    sims = 1000
    for i in range(0, dte):
      random = tf.random.normal(shape=[dte, sims], mean=0.0, 
                                stddev=1.0, dtype=tf.float64)
      scale = daily_r - tf.cast(0.5, tf.float64) * (
        predicted_Y_mean + tf.math.sqrt(predicted_Y_var) * random
      )
      ln_S = tf.math.log(spot) + tf.math.cumsum(scale, axis=0)

    S = tf.math.exp(ln_S)
    payoffs = np.maximum(S[-1] - K, 0)
    option_price = np.mean(payoffs) * np.exp(-r * (dte / 365))
    # _todo update task state
    return option_price
  
  def OptionsPricing(self, strike_prices: List[float], 
                    expire_dates: List[datetime], 
                    current_date: datetime) -> List[float]:
    assert not (len(strike_prices) > 1 and len(expire_dates) > 1)
    assert current_date == self.end_date
    spot = get_spot_ticker(self.ticker, current_date)
    r = get_r(current_date)
    prices = []
    for strike_price in strike_prices:
      for expire_date in expire_dates:
        prices.append(self.OptionPricing(spot, strike_price, expire_date, 
                                         current_date, r))
        self.task.update_state(state="CALCULATING", meta={"current": len(prices), 
                        "total": len(strike_prices)*len(expire_dates)})
        
    return prices