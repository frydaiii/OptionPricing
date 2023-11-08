from datetime import datetime
from fastapi import Depends
from matplotlib import pyplot as plt
from sqlalchemy import select
from sqlalchemy.orm import Session
from back.models import Option2019
from back.calculators import calculate_bs_2, calculate_mc_2, get_r, get_spot, \
        get_volatility, get_volatility_ticker, get_spot_ticker, \
            get_d_oprice_values, calculate_garch
import numpy as np
from back.cache import pricing
from back.plot import save_img
from back.gaussian.process import calculate_gp

async def calculate_prices_job(client_key: str,
    ticker: str, 
    strike: float, 
    selected_date: str, expire_date: str,
    db: Session):

    price = await pricing.get(client_key)

    # get data
    spot = get_spot(selected_date)
    r = get_r(selected_date)
    vol = get_volatility(selected_date)

    strike_prices = [] # from db
    expire_dates = [] # from db
    query = (
        select(Option2019)
        .where(Option2019.underlying == ticker)
        .where(Option2019.quotedate == selected_date)
        .where(Option2019.volume > 0)
        .where(Option2019.type == "call")
    )
    if expire_date != "":
        query = (query
                 .where(Option2019.expiration == expire_date)
                 .order_by(Option2019.strike))
        
        data = db.execute(query)
        data = data.scalars().all()
        price["mk"] = [opt.last for opt in data]
        strike_prices = [int(opt.strike) for opt in data]
        expire_date = datetime.strptime(expire_date, "%Y-%m-%d").date()
        price["garch"] = calculate_garch(strike_prices, [expire_date], selected_date, r)
        await calculate_gp(client_key, strike_prices, [expire_date], selected_date, ticker)
        for strike_price in strike_prices:
            price["bs"].append(
                calculate_bs_2(spot, strike_price, expire_date, selected_date, r, vol))
            price["mc"].append(
                calculate_mc_2(spot, strike_price, expire_date, selected_date, r, vol))
            bs_ivo, _ = get_d_oprice_values(spot, strike_price, expire_date, selected_date, r, vol)
            price["bs_ivo"].append(bs_ivo)
            await pricing.set(client_key, price) # update cache

    else:
        query = (query
                 .where(Option2019.strike == strike)
                 .order_by(Option2019.expiration))
        data = db.execute(query)
        data = data.scalars().all()
        price["mk"] = [opt.last for opt in data]
        expire_dates = [opt.expiration for opt in data]
        price["garch"] = calculate_garch([strike], expire_dates, selected_date, r)
        await calculate_gp(client_key, [strike], expire_dates, selected_date, ticker)
        for expire_date in expire_dates:
            price["bs"].append(
                calculate_bs_2(spot, strike, expire_date, selected_date, r, vol))
            price["mc"].append(
                calculate_mc_2(spot, strike, expire_date, selected_date, r, vol))
            bs_ivo, _ = get_d_oprice_values(spot, strike, expire_date, selected_date, r, vol)
            price["bs_ivo"].append(bs_ivo)
            await pricing.set(client_key, price) # update cache
    
    # plot and save to image
    price = await pricing.get(client_key)
    prices_bs = price["bs"]
    prices_mc = price["mc"]
    prices_garch = price["garch"]
    prices_bs_ivolatility = price["bs_ivo"]
    prices_gp = price["gp"]
    market_prices = price["mk"]

    price["img1"], price["img2"] = save_img(client_key, prices_bs, prices_mc, 
                                            prices_garch, prices_bs_ivolatility, 
                                            prices_gp,
                                            market_prices, strike_prices, expire_dates)
    price["is_done"] = True
    await pricing.set(client_key, price) # udpate cache
    return
