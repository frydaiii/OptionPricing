from math import sqrt, log, exp, erf
from datetime import datetime

def OptionPricing(S: float, K: float, expire_date: datetime, 
                  current_date: datetime, r: float, vol: float):
  T = (expire_date - current_date).days/365
  VqT = vol * sqrt(T)
  d1 = (log(S / K) + (r + .5*vol*vol) * T) / VqT
  d2 = d1 - VqT
  n1 = .5 + .5 * erf(d1 * 1./sqrt(2.))
  n2 = .5 + .5 * erf(d2 * 1./sqrt(2.))
  eRT = exp(-r * T)
  return S * n1 - K * eRT * n2 # Call price
  # Put price = (K * eRT * (1.-n2) - S * (1.-n1))
