from worker.main import app, rd
from back.utils import *
import json
from back.black_scholes import OptionPricing
from datetime import datetime
import numpy as np


@app.task(bind=True)
# _todo rename
def calculate(self,
              type: str,
              strike_prices: [],
              expire_dates: [],
              current_date: datetime,
              ticker="^SPX"):

  end_date = current_date
  start_date = end_date - timedelta(days=365 * 10)
  stock_data, r = get_price_and_r(start_date, end_date, ticker)
  r = r[-1]
  spot = stock_data["Close"].iloc[-1]
  log_return = np.log1p(stock_data["Close"].pct_change().dropna().to_numpy())
  vol = np.std(log_return) * np.sqrt(252)

  option_prices = []
  for strike_price in strike_prices:
    for expire_date in expire_dates:
      option_prices.append(
          OptionPricing(type, spot, strike_price, expire_date, current_date, r,
                        vol))
  rd.set(self.request.id, json.dumps(option_prices))


@app.task(bind=True)
def CalculateSingle(self, type: str, spot: float, strike: float,
                    current: datetime, expire: datetime, r: float, vol: float):
  price = OptionPricing(type, spot, strike, expire, current, r, vol)
  rd.set(self.request.id, price)
