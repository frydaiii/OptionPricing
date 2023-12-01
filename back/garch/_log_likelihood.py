import numpy as np
from typing import List
import math


class LogLikelihooMixin(object):

  def Variance(self, parameters: []):
    "Returns the variance expression of a GARCH(1,1) process."

    # Slicing the parameters list
    omega = parameters[0]
    alpha = parameters[1]
    beta = parameters[2]
    lambd = parameters[3]

    # Length of log_returns
    length = len(self.log_returns)

    # Initializing an empty array
    sigma_2 = np.zeros(length)

    # Filling the array, if i == 0 then uses the long term variance.
    for i in range(length):
      if i == 0:
        # sigma_2[i] = omega / (1 - alpha * (1 + lambd**2) - beta)
        sigma_2[i] = np.std(self.log_returns)**2
      else:
        epsilon_prev = self.log_returns[
            i - 1] - self.r[i-1] / 365 + 0.5 * sigma_2[i - 1]
        sigma_2[i] = (omega + alpha *
                      (epsilon_prev - lambd * math.sqrt(sigma_2[i - 1]))**2 +
                      beta * sigma_2[i - 1])

    return sigma_2

  def LogLikelihood(self, parameters: []):
    "Defines the log likelihood sum to be optimized given the parameters."

    sigma_2 = self.Variance(parameters)
    daily_r = self.r / 365
    lambd = parameters[3]
    n = len(self.log_returns)

    loglikelihood = 0.5*n*np.log(2*math.pi) + 0.5 * np.sum(
        np.log(sigma_2) +
        (self.log_returns - daily_r - lambd * np.sqrt(sigma_2) +
         0.5 * sigma_2)**2 / sigma_2)
    return loglikelihood
