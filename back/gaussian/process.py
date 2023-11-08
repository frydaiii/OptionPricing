import numpy as np
import tensorflow as tf
import gpflow
import yfinance as yf
from datetime import datetime, timedelta
from gpflow.models import SVGP
from gpflow import default_float, kernels, likelihoods
from check_shapes import inherit_check_shapes
from gpflow.base import TensorType
from tensorflow_probability import distributions as tfd
from back.utils import get_data, get_r, get_close_price_r, get_spot
from back.gaussian.likelihoods import ExpGaussian
from gpflow.ci_utils import reduce_in_tests
from back.gaussian.optimizers import run_adam, run_natgrad
from back.cache import pricing
from celery import Task

# async def calculate_gp(client_key, strike_prices, expire_dates, current_date, ticker = "^SPX"):
#     assert not (len(strike_prices) > 1 and len(expire_dates) > 1)

#     # _todo update this
#     for i in range(0, len(expire_dates)):
#         if type(expire_dates[i]) is str:
#             expire_dates[i] = datetime.strptime(expire_dates[i], "%Y-%m-%d").date()
#     if type(current_date) is str:
#         current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
#     if ticker == "SPX" or ticker == "" or ticker == "SPXW":
#         ticker = "^SPX"

#     price = await pricing.get(client_key)
#     await pricing.set(client_key, price) # update cache
#     # prepare data
#     start_date = current_date - timedelta(days=5*365)
#     end_date = current_date
#     X, Y, N = gen_data(start_date, end_date)
#     spot = get_spot(end_date)
#     r = get_r(end_date)

#     model = train(client_key, X, Y, N)

#     for strike_price in strike_prices:
#         for expire_date in expire_dates:
#             price["gp"].append(option_pricing(model, N, spot, 
#                                          strike_price, expire_date, current_date, r))
#             await pricing.set(client_key, price) # update cache
            
#     return

def gen_data(start_date, end_date, ticker):
    df_close, r = get_close_price_r(start_date, end_date, ticker)
    daily_r = r/360
    Y = tf.convert_to_tensor(2*daily_r-2*df_close.pct_change().dropna().to_numpy())
    N = len(Y)
    X = tf.cast(tf.range(N), tf.float64)
    # training data
    X = tf.expand_dims(X, axis=1)
    Y = tf.expand_dims(Y, axis=1)

    return (X, Y, N)

def train(task: Task, X, Y, N):
    # Create SVGP model with squared exponential kernel and likelihood.
    M = 20  # Number of inducing locations
    idx = [int(i) for i in list(np.linspace(0, N, M, endpoint=False))]
    Z = X.numpy()[idx, :].copy()  # Initialize inducing locations to the first M inputs in the dataset
    model = SVGP(kernel=kernels.SquaredExponential(), likelihood=ExpGaussian(),
                 inducing_variable=Z,num_data=N, 
                 mean_function=gpflow.functions.Constant(-10))
    gpflow.set_trainable(model.inducing_variable, True)
    minibatch_size = 100
    train_dataset = tf.data.Dataset.from_tensor_slices((X.numpy(), Y.numpy())).repeat().shuffle(N)
    train_iter = iter(train_dataset.batch(minibatch_size))

    # Specify the number of optimization steps.
    maxiter_adam = reduce_in_tests(30000)
    maxiter_natgrad = reduce_in_tests(10000)
    # Perform optimization.
    run_adam(task, model, maxiter_adam, train_iter)
    run_natgrad(task, model, maxiter_natgrad, train_iter)

    return model

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