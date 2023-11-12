from worker.main import app
from back.gaussian.main import GaussianProcess
from datetime import datetime
from back.utils import *
from worker.main import rd
import json
from typing import List


@app.task(bind=True)
def calculate(self,
              strike_prices: List[float],
              expire_dates: List[datetime],
              current_date: datetime,
              ticker="^SPX"):
  assert not (len(strike_prices) > 1 and len(expire_dates) > 1)
  
  # prepare data
  start_date = current_date - timedelta(days=5 * 365)
  end_date = current_date

  model = GaussianProcess(self)
  model.InitializeData(start_date, end_date, ticker)
  model.Train()
  option_prices = model.OptionsPricing(strike_prices, expire_dates,
                                       current_date)

  rd.set(self.request.id, json.dumps(option_prices))
  return
