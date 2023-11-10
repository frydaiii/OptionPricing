from worker.main import rd
import json
from celery.result import AsyncResult


def handle_calculate_price_status(bs_id: str,
                                   gp_id: str = "",
                                   garch_id: str = ""):
  bs_result = AsyncResult(bs_id)
  response = {}
  if bs_result.successful():
    response["bs"] = rd.get(bs_id)

  if garch_id != "":
    garch_result = AsyncResult(garch_id)
    if garch_result.successful():
      response["garch"] = json.loads(rd.get(garch_id))
    else:
      response["garch"] = {
          "state": garch_result.state,
          "info": garch_result.info,
      }
  if gp_id != "":
    gp_result = AsyncResult(gp_id)
    if gp_result.successful():
      response["gp"] = json.loads(rd.get(gp_id))
    else:
      response["gp"] = {
          "state": gp_result.state,
          "info": gp_result.info,
      }

  return response
