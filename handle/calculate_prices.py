# handle request from /calculate-price-2
from worker import gp, garch, bs
from worker.main import rd
from datetime import datetime
from fastapi import Depends
from matplotlib import pyplot as plt
from sqlalchemy import select
from sqlalchemy.orm import Session
from back.models import Option2019
import json
import uuid
# from back.gaussian.process import calculate_gp


def handle_calculate_prices(db: Session, strike: float, current_date: datetime,
                            expire_date: datetime, ticker: str):
  expire_dates = []
  strike_prices = []
  market_prices = []
  query = (select(Option2019).where(Option2019.underlying == ticker).where(
      Option2019.quotedate == current_date.strftime("%Y-%m-%d")).where(
          Option2019.volume > 0).where(Option2019.type == "call"))
  if expire_date != "":
    query = (query.where(
        Option2019.expiration == expire_date.strftime("%Y-%m-%d")).order_by(
            Option2019.strike))

    data = db.execute(query)
    data = data.scalars().all()
    strike_prices = [int(opt.strike) for opt in data]
    market_prices = [opt.last for opt in data]
    expire_dates = [expire_date]
  else:
    query = (query.where(Option2019.strike == strike).order_by(
        Option2019.expiration))
    data = db.execute(query)
    data = data.scalars().all()
    expire_dates = [
        datetime.strptime(opt.expiration, "%Y-%m-%d") for opt in data
    ]
    market_prices = [opt.last for opt in data]
    strike_prices = [strike]

  if ticker == "SPX" or ticker == "SPXW" or ticker == "":
    ticker = "^SPX"

  gp_task = gp.calculate.delay(strike_prices, expire_dates, current_date,
                               ticker)
  garch_task = garch.calculate.delay(strike_prices, expire_dates, current_date,
                                     ticker)
  bs_task = bs.calculate.delay(strike_prices, expire_dates, current_date,
                               ticker)
  market_id = str(uuid.uuid4())
  market_info = {
      "prices": market_prices,
      "strikes": strike_prices,
      "expire_dates": [date.strftime('%d/%m/%Y') for date in expire_dates]
  }
  rd.set(market_id, json.dumps(market_info))
  return {
      "market_id": market_id,
      "gp_id": gp_task.id,
      "garch_id": garch_task.id,
      "bs_id": bs_task.id
  }
