# handle request from /calculate-price
from worker import gp, garch, bs
from datetime import datetime
from back.utils import get_spot_ticker, get_volatility_ticker, get_r


def handle_calculate_price(spot: float,
                           strike: float,
                           current_date: datetime,
                           expire_date: datetime,
                           r: float,
                           v: float,
                           ticker: str = ""):
  if ticker == "": # _todo use garch to cal vol
    bs_task = bs.CalculateSingle.delay(spot, strike, current_date, expire_date,
                                       r, v)
    return {"bs_id": bs_task.id}
  else:
    if ticker == "SPX" or ticker == "SPXW" or ticker == "":
      ticker = "^SPX"
    r = get_r(current_date)
    v = get_volatility_ticker(ticker, current_date)
    spot = get_spot_ticker(ticker, current_date)
    bs_task = bs.CalculateSingle.delay(spot, strike, current_date, expire_date,
                                       r, v)
    gp_task = gp.calculate.delay([strike], [expire_date], current_date, ticker)
    garch_task = garch.calculate.delay([strike], [expire_date], current_date,
                                       ticker)
    return {
        "gp_id": gp_task.id,
        "garch_id": garch_task.id,
        "bs_id": bs_task.id
    }
