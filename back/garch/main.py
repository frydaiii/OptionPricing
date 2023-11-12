import numpy as np
import scipy
from datetime import datetime
from back.utils import get_price_and_r
from back.garch._log_likelihood import LogLikelihooMixin
from back.garch._pricing import PricingMixin
from celery import Task
from typing import List

# us_risk_prem = {
#     "2009": 0.051,
#     "2010": 0.051,
#     "2011": 0.055,
#     "2012": 0.055,
#     "2013": 0.057,
#     "2014": 0.054,
#     "2015": 0.055,
#     "2016": 0.053,
#     "2017": 0.057,
#     "2018": 0.054,
#     "2019": 0.056,
#     "2020": 0.056,
#     "2021": 0.055,
#     "2022": 0.056,
#     "2023": 0.057,
# }


# this class implement GARCH(1, 1)
class GARCH(LogLikelihooMixin, PricingMixin):

  def __init__(self, task: Task):
    self.log_returns = None
    self.r = None
    self.params = []  # [omega, alpha, beta, lambd]
    self.ticker = ""
    self.task = task  # celery task for update state

  def InitializeData(self, start_date: datetime, end_date: datetime,
                     ticker: str):
    stock_data, r = get_price_and_r(start_date, end_date, ticker)
    self.log_returns = stock_data["Close"].pct_change().dropna().to_numpy()
    self.r = r
    self.ticker = ticker

  def IncorrectUnconditionalVariance(self):
    omega = self.params[0]
    alpha = self.params[1]
    beta = self.params[2]
    return omega * (1 - alpha - beta)

  def Optimize(self):
    "Optimizes the log likelihood function and returns estimated coefficients"
    self.task.update_state("OPTIMIZING")
    # Parameters initialization
    parameters = [0, 0, 0, 0]

    def Constraint(params):
      alpha = params[1]
      beta = params[2]
      lambd = params[3]
      return 1 - alpha * (1 + lambd**2) - beta

    opt = scipy.optimize.minimize(self.LogLikelihood,
                                  parameters,
                                  bounds=((1e-10, None), (1e-10, None),
                                          (1e-10, None), (1e-10, None)))

    if Constraint(opt.x) <= 0:
      # I use this to check params value, because add constraints to minimize 
      # function cause some problem
      raise ValueError("Parameters does not valid")

    self.params = opt.x
    return
