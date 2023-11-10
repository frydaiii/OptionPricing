from worker.main import app, rd
from back.utils import *
import json
from back.black_scholes import OptionPricing
from datetime import datetime

@app.task(bind=True)
# def calculate(self, spot, strike_prices, expired_dates, current_date, r, vol):
def calculate(self, strike_prices:[], expire_dates: [], current_date: datetime, ticker = "^SPX"):
  spot = get_spot_ticker(ticker, current_date)
  r = get_r(current_date)
  vol = get_volatility_ticker(ticker, current_date)
  option_prices = []
  for strike_price in strike_prices:
    for expire_date in expire_dates:
      option_prices.append(OptionPricing(spot, strike_price, expire_date, 
                                          current_date, r, vol))
  rd.set(self.request.id, json.dumps(option_prices))