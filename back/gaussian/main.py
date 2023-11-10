import numpy as np
import tensorflow as tf
import gpflow
from datetime import datetime
from gpflow.models import SVGP
from gpflow import kernels
from back.utils import get_price_and_r
from back.gaussian.likelihoods import ExpGaussian
from gpflow.ci_utils import reduce_in_tests
from back.gaussian._optimizers import OptiomizerMixin
from back.gaussian._pricing import PricingMixin
from celery import Task


class GaussianProcess(OptiomizerMixin, PricingMixin):
  def __init__(self, task: Task):
    # model component
    self.X = None
    self.Y = None
    self.N = None
    self.model = None

    # range of data
    self.start_date = None
    self.end_date = None
    self.ticker = ""
    self.task = task # celery task for update status

  def InitializeData(self, start_date: datetime, 
                     end_date: datetime, ticker: str):
    stock_data, r = get_price_and_r(start_date, end_date, ticker)
    daily_r = r / 360
    self.start_date = start_date
    self.end_date = end_date
    self.ticker = ticker

    # init X, Y, N
    Y = tf.convert_to_tensor(
      2 * daily_r - 2 * stock_data["Close"].pct_change().dropna().to_numpy()
    )
    self.N = len(Y)
    X = tf.cast(tf.range(self.N), tf.float64)
    self.X = tf.expand_dims(X, axis=1)
    self.Y = tf.expand_dims(Y, axis=1)

    # init model with squared exponential kernel and likelihood.
    M = 20  # number of inducing locations
    idx = [int(i) for i in list(np.linspace(0, self.N, M, endpoint=False))]
    Z = self.X.numpy()[idx, :].copy() # inducing locations
    self.model = SVGP(
      kernel=kernels.SquaredExponential(),
      likelihood=ExpGaussian(),
      inducing_variable=Z,
      num_data=self.N,
      mean_function=gpflow.functions.Constant(-10),
    )

  def Train(self):
    gpflow.set_trainable(self.model.inducing_variable, True)
    minibatch_size = 100
    train_dataset = (
      tf.data.Dataset.from_tensor_slices((self.X.numpy(), self.Y.numpy()))
      .repeat()
      .shuffle(self.N)
    )
    train_iter = iter(train_dataset.batch(minibatch_size))

    # Specify the number of optimization steps.
    maxiter_adam = reduce_in_tests(30000)
    maxiter_natgrad = reduce_in_tests(10000)
    # Perform optimization.
    self.RunAdam(maxiter_adam, train_iter)
    self.RunNatGrad(maxiter_natgrad, train_iter)
