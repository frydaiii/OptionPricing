import numpy as np
import scipy
from datetime import datetime
from back.utils import get_price_and_r
from back.garch._log_likelihood import LogLikelihooMixin
from back.garch._pricing import PricingMixin
from celery import Task


us_risk_prem = {
    "2009": 0.051,
    "2010": 0.051,
    "2011": 0.055,
    "2012": 0.055,
    "2013": 0.057,
    "2014": 0.054,
    "2015": 0.055,
    "2016": 0.053,
    "2017": 0.057,
    "2018": 0.054,
    "2019": 0.056,
    "2020": 0.056,
    "2021": 0.055,
    "2022": 0.056,
    "2023": 0.057,
}

# this class implement GARCH(1, 1)
class GARCH(LogLikelihooMixin, PricingMixin):
  def __init__(self, task: Task):
    self.log_returns = None
    self.r = None
    self.lamb = []
    self.params = []  # [omega, alpha, beta]
    self.ticker  = ""
    self.task = task # celery task for update state

  def InitializeData(self, start_date: datetime, end_date: datetime, 
                     ticker: str):
    stock_data, r = get_price_and_r(start_date, end_date, ticker)
    self.log_returns = stock_data["Close"].pct_change().dropna().to_numpy()
    self.r = r
    self.lamb = []
    self.ticker = ticker
    for date in stock_data["Date"]:
      self.lamb.append(us_risk_prem[str(date.year)])

  def Optimize(self):
    "Optimizes the log likelihood function and returns estimated coefficients"
    self.task.update_state("OPTIMIZING")
    # Parameters initialization
    parameters = [0, 0, 0]

    # Parameters optimization, scipy does not have a maximize function, so we minimize the opposite of the equation described earlier
    opt = scipy.optimize.minimize(
      self.LogLikelihood, parameters, bounds=((0.001, 1), (0.001, 1), (0.001, 1))
    )

    variance = (
      0.01**2 * opt.x[0] / (1 - opt.x[1] - opt.x[2])
    )  # Times .01**2 because it concerns squared returns

    self.params = parameters # _todo check value of this, currently it's wrong
    return np.append(opt.x, variance)
