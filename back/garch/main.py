import numpy as np
import scipy
from datetime import datetime
from back.utils import get_price_and_r
from back.garch._log_likelihood import LogLikelihooMixin
from back.garch._pricing import PricingMixin
from typing import List


# this class implement GARCH(1, 1)
class GARCH(LogLikelihooMixin, PricingMixin):

  def __init__(self):
    self.log_returns = None
    self.r = None
    self.params = []  # [omega, alpha, beta, lambd]
    self.ticker = ""

  def InitializeData(self, start_date: datetime, end_date: datetime,
                     ticker: str):
    stock_data, r = get_price_and_r(start_date, end_date, ticker)
    self.log_returns = np.log1p(
        stock_data["Close"].pct_change().dropna().to_numpy())
    self.r = r
    self.ticker = ticker

  def IncorrectUnconditionalVariance(self):
    omega = self.params[0]
    alpha = self.params[1]
    beta = self.params[2]
    return omega * (1 - alpha - beta)

  def Optimize(self):
    "Optimizes the log likelihood function and returns estimated coefficients"
    # Parameters initialization
    print("Optimizing the log likelihood function")
    parameters = [0.1, 0.92, 0.05, 0]

    def Constraint(params):
      alpha = params[1]
      beta = params[2]
      lambd = params[3]
      return 1 - alpha * (1 + lambd**2) - beta

    opt = scipy.optimize.minimize(self.LogLikelihood,
                                  parameters,
                                  bounds=((1e-10, None), (0, None),
                                          (0, None), (0, 1)),
                                          method="Nelder-Mead")

    if Constraint(opt.x) <= 0:
      # I use this to check params value, because add constraints to minimize
      # function cause some problem
      raise ValueError("Parameters does not valid")

    self.params = opt.x
    return
