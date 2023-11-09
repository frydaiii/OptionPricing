from worker.main import rd
import json
from celery.result import AsyncResult
from back.plot import save_img_2

def handle_calculate_prices_status(gp_id, garch_id, mc_id, bs_ivo_id, market_id):
    gp_result = AsyncResult(gp_id)
    garch_result = AsyncResult(garch_id)
    mc_result = AsyncResult(mc_id)
    bs_ivo_result = AsyncResult(bs_ivo_id)
    market_result = AsyncResult(market_id)

    if (gp_result.successful() and garch_result.successful() and mc_result.successful() 
        and bs_ivo_result.successful()):

        gp_prices = json.loads(rd.get(gp_id))
        garch_prices = json.loads(rd.get(garch_id))
        mc_prices = json.loads(rd.get(mc_id))
        bs_ivo_prices = json.loads(rd.get(bs_ivo_id))
        market_info = json.loads(rd.get(market_id))

        market_prices = market_info["prices"]
        strike_prices = market_info["strikes"]
        expire_dates = market_info["expire_dates"]
        img1, img2 = save_img_2(market_id, mc_prices, 
                                        garch_prices, bs_ivo_prices, 
                                        gp_prices,
                                        market_prices, strike_prices, expire_dates)
        
        return {
                "success": True,
                "img1": img1,
                "img2": img2
        }
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
            "mc": {
                "state": mc_result.state,
            },
            "bs_ivo": {
                "state": bs_ivo_result.state,
            },
        }
