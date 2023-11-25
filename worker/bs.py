from worker.main import app, rd
from back.utils import *
import json
from back.black_scholes import OptionPricing
from datetime import datetime
from back.garch.main import GARCH


@app.task(bind=True)
# _todo rename
def calculate(self,
              type: str,
              strike_prices: [],
              expire_dates: [],
              current_date: datetime,
              ticker="^SPX"):
  spot = get_spot_ticker(ticker, current_date)
  r = get_r(current_date)

  # get volatility
  end_date = current_date
  start_date = end_date - timedelta(days=365 * 10)
  model = GARCH(self)
  model.InitializeData(start_date, end_date, ticker)
  model.Optimize()
  vol = math.sqrt(model.IncorrectUnconditionalVariance() * 365)

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
