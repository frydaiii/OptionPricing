from worker.main import app
from datetime import datetime
from back.utils import *
from worker.main import rd
from datetime import timedelta, datetime
import numpy as np
from back.utils import *
from statistics import variance
import json
from back.garch.main import GARCH
from typing import List


def calculate(self,
              type: str,
              strike_prices: List[float],
              expire_dates: List[datetime],
              current_date: datetime,
              ticker=""):
  assert not (len(strike_prices) > 1 and len(expire_dates) > 1)

  # get historical data of spx
  end_date = current_date
  start_date = end_date - timedelta(days=365 * 10)

  model = GARCH(self)
  model.InitializeData(start_date, end_date, ticker)
  model.Optimize()
  H0 = model.Variance(model.params)[-1]  # last estimated conditional variance
  option_prices = model.OptionsPricing(type, H0, strike_prices, expire_dates,
                                       current_date)

  rd.set(self.request.id, json.dumps(option_prices))
  return
