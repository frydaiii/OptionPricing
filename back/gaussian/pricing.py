from datetime import datetime
import tensorflow as tf
import numpy as np

def option_pricing(model, N, spot, strike_price, expire_date, current_date, r):
  if type(expire_date) is str:
    expire_date = datetime.strptime(expire_date, "%Y-%m-%d")
  dte = (expire_date - current_date).days
  X_star = tf.cast(tf.range(N, N + dte), tf.float64)
  X_star = tf.expand_dims(X_star, axis=1)
  predicted_Y_mean, predicted_Y_var = model.predict_y(X_star)

  spot = tf.cast(spot, tf.float64)
  K = tf.cast(strike_price, tf.float64)
  daily_r = r/360
  sim_prices = []
  sims = 1000
  for i in range(0, dte):
    random = tf.cast(tf.random.normal(shape=[dte, sims], mean=0.0, stddev=1.0), tf.float64)
    scale = tf.cast(daily_r, tf.float64)-tf.cast(0.5, tf.float64)*(predicted_Y_mean+tf.math.sqrt(predicted_Y_var)*random)
    ln_S = tf.math.log(spot) + tf.math.cumsum(scale, axis=0)

  S = tf.math.exp(ln_S)
  payoffs = np.maximum(S[-1]-K, 0)
  option_price = np.mean(payoffs)*np.exp(-r*(dte/365))
  return option_price