from worker.main import app
from back.gaussian.process import gen_data, train, option_pricing
from datetime import datetime
from back.utils import *
from worker.main import rd
import json

@app.task(bind=True)
def calculate(self, strike_prices: [], expire_dates: [], current_date, ticker = "^SPX"):
    assert not (len(strike_prices) > 1 and len(expire_dates) > 1)

    # _todo update this
    for i in range(0, len(expire_dates)):
        if type(expire_dates[i]) is str:
            expire_dates[i] = datetime.strptime(expire_dates[i], "%Y-%m-%d").date()
    if type(current_date) is str:
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
    if ticker == "SPX" or ticker == "" or ticker == "SPXW":
        ticker = "^SPX"

    self.update_state(state="STARTED")
    # prepare data
    start_date = current_date - timedelta(days=5*365)
    end_date = current_date
    X, Y, N = gen_data(start_date, end_date, ticker)
    spot = get_spot(end_date)
    r = get_r(end_date)

    model = train(self, X, Y, N)

    option_prices = []
    for strike_price in strike_prices:
        for expire_date in expire_dates:
            option_prices.append(option_pricing(model, N, spot, 
                                         strike_price, expire_date, current_date, r))
            self.update_state(state="CALCULATING", meta={"current": len(option_prices), 
                                                         "total": len(strike_prices)*len(expire_dates)})
    rd.set(self.request.id, json.dumps(option_prices))
    return