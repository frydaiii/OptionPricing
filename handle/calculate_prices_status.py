from worker.main import rd
import json
from celery.result import AsyncResult
from back.plot import save_img


def handle_calculate_prices_status(gp_id: str, garch_id: str, bs_id: str,
                                   market_id: str):
  gp_result = AsyncResult(gp_id)
  garch_result = AsyncResult(garch_id)
  bs_result = AsyncResult(bs_id)

  if (gp_result.successful() and garch_result.successful()
      and bs_result.successful()):

    gp_prices = json.loads(rd.get(gp_id))
    garch_prices = json.loads(rd.get(garch_id))
    bs_prices = json.loads(rd.get(bs_id))
    market_info = json.loads(rd.get(market_id))

    market_prices = market_info["prices"]
    strike_prices = market_info["strikes"]
    expire_dates = market_info["expire_dates"]
    img1, img2 = save_img(market_id, garch_prices, bs_prices, gp_prices,
                          market_prices, strike_prices, expire_dates)

    return {"success": True, "img1": img1, "img2": img2}
  else:
    return {
        "success": False,
        "gp": {
            "state": gp_result.state,
            "info": gp_result.info,
        },
        "garch": {
            "state": garch_result.state,
            "info": garch_result.info,
        },
        "bs": {
            "state": bs_result.state,
        },
    }
