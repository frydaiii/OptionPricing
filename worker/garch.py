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

# US average market risk premium
# https://www.statista.com/statistics/664840/average-market-risk-premium-usa/
us_risk_prem = {
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

@app.task(bind=True)
# def calculate(self, strike_prices: [], expire_dates: [], current_date, r, ticker = ""):
def calculate(self, strike_prices: List[float], expire_dates: List[datetime], 
              current_date: datetime, ticker = ""):
  assert not (len(strike_prices) > 1 and len(expire_dates) > 1)
  # expire_date = "2022-12-16"
  # for i in range(0, len(expire_dates)):
  #   expire_dates[i] = expire_dates[i].date()
  # current_date = current_date.date()
  if ticker == "SPX" or ticker == "" or ticker == "SPXW":
    ticker = "^SPX"

  # get historical data of spx
  end_date = current_date
  start_date = end_date - timedelta(days=365 * 10)

  model = GARCH(self)
  model.InitializeData(start_date, end_date, ticker)
  model.Optimize()
  option_prices = model.OptionsPricing(strike_prices, expire_dates, current_date)

  # stock_data = get_data(start_date, end_date, ticker)
      
  # df_close = stock_data["Close"]
  # df_return = df_close.pct_change().dropna()
  # r = get_r(current_date)
  # stock_data, r = get_price_and_r(start_date, end_date, ticker)
  # df_return = stock_data["close"].pct_change().dropna()

  # # init and fit model
  # self.update_state(state="OPTIMIZING")
  # daily_r = r / 360 # the input param is risk free rate in a year
  # lbd = us_risk_prem[str(current_date.year)]  # _todo pls update this
  # model = garch_1_1(df_return.to_numpy(), daily_r, lbd)
  # model.optimize()

  # # generate array of annual volatility, include in and out-sample
  # omega = model.params[0]
  # alpha = model.params[1]
  # beta = model.params[2]
  # H0 = variance(df_return)

  # # monte carlo simulation
  # option_prices = []
  # assert ((len(strike_prices) == 1 and len(expire_dates) == 1) # single option
  #     or (len(strike_prices) == 1 and len(expire_dates) > 1) # multiple options
  #     or (len(strike_prices) > 1 and len(expire_dates) == 1)) # multiple options
  # for strike_price in strike_prices:
  #     for expire_date in expire_dates:
  #         dte = (expire_date - current_date).days
  #         T = dte / 365
  #         steps = dte
  #         num_simulations = 1000
  #         Z = np.random.normal(size=(steps + 1, num_simulations))
  #         H = np.empty(shape=(steps, num_simulations))
  #         H = np.concatenate((np.full(shape=(1, num_simulations), fill_value=H0), H))
  #         lnS = np.empty(shape=(steps, num_simulations))
  #         lnS = np.concatenate(
  #             (np.full(shape=(1, num_simulations), fill_value=np.log(df_close.iloc[-1])), lnS)
  #         )
  #         for i in range(1, steps + 1):
  #             # _todo this formula could be improved
  #             H[i] = omega + (alpha * (Z[i - 1] - lbd) ** 2 + beta) * H[i - 1]
  #             lnS[i] = lnS[i - 1] + daily_r - 0.5 * H[i] + Z[i] * np.sqrt(H[i])

  #         paths = np.exp(lnS)
  #         payoffs = np.maximum(paths[-1] - strike_price, 0)
  #         option_price = np.mean(payoffs) * np.exp(-r * T)  # discounting back to present value
  #         option_prices.append(option_price)
  #         self.update_state(state="CALCULATING", meta={"current": len(option_prices), 
  #                                                       "total": len(strike_prices)*len(expire_dates)})
  rd.set(self.request.id, json.dumps(option_prices))
  return 