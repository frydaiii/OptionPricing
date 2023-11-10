from worker.main import app, rd
from back.calculators import calculate_mc_2
from back.utils import *
import json

# _todo delete this file
@app.task(bind=True)
# def calculate(self, spot, strike_prices, expired_dates, current_date, r, vol):
def calculate(self, strike_prices:[], expire_dates: [], current_date, ticker = "^SPX"):
    spot = get_spot_ticker(ticker, current_date)
    r = get_r(current_date)
    vol = get_volatility_ticker(ticker, current_date)
    option_prices = []
    for strike_price in strike_prices:
        for expire_date in expire_dates:
            option_prices.append(calculate_mc_2(spot, strike_price, 
                                                expire_date, current_date, r, vol))
    rd.set(self.request.id, json.dumps(option_prices))
    