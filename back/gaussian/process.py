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
from back.utils import get_data, get_r
from back.gaussian.likelihoods import ExpGaussian
from gpflow.ci_utils import reduce_in_tests
from back.gaussian.optimizers import run_adam, run_natgrad
from back.cache import pricing
from back.gaussian.pricing import option_pricing

async def calculate_gp(client_key, strike_prices, expire_dates, current_date, ticker = "^SPX"):
    assert ((len(strike_prices) == 1 and len(expire_dates) == 1) # single option
    or (len(strike_prices) == 1 and len(expire_dates) > 1) # multiple options
    or (len(strike_prices) > 1 and len(expire_dates) == 1)) # multiple options

    for i in range(0, len(expire_dates)):
        if type(expire_dates[i]) is str:
            expire_dates[i] = datetime.strptime(expire_dates[i], "%Y-%m-%d").date()
    if type(current_date) is str:
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
    if ticker == "SPX" or ticker == "" or ticker == "SPXW":
        ticker = "^SPX"

    price = await pricing.get(client_key)
    await pricing.set(client_key, price) # update cache
    # prepare data
    start_date = current_date - timedelta(days=5*365)
    end_date = current_date
    stock_data = get_data(start_date, end_date, ticker)
    df_close = stock_data["Close"]
    r = get_r(end_date)
    daily_r = r/360
    Y = tf.convert_to_tensor(2*daily_r-2*df_close.pct_change().dropna().to_numpy())
    N = len(Y)
    X = tf.cast(tf.range(N), tf.float64)

    # training data
    X = tf.expand_dims(X, axis=1)
    Y = tf.expand_dims(Y, axis=1)

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
    await run_adam(client_key, model, maxiter_adam, train_iter)
    await run_natgrad(client_key, model, maxiter_natgrad, train_iter)

    for strike_price in strike_prices:
        for expire_date in expire_dates:
            price["gp"].append(option_pricing(model, N, df_close.iloc[-1], 
                                         strike_price, expire_date, current_date, r))
            await pricing.set(client_key, price) # update cache
            
    return