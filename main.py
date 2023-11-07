from datetime import datetime
from fastapi import FastAPI, Request, Depends, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from databases import Database
from matplotlib import pyplot as plt
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
from back.models import Option2019
from back.calculators import calculate_bs_2, calculate_mc_2, get_r, get_spot, \
        get_volatility, get_volatility_ticker, get_spot_ticker, \
            get_d_oprice_values, calculate_garch
import yfinance as yf
import QuantLib as ql
import numpy as np
import math
import uvicorn
import os

# Define database URL
DATABASE_URL = "mysql+pymysql://root:1@localhost:3306/option_chains"

# Create a database instance
database = Database(DATABASE_URL)

engine = create_engine(DATABASE_URL)
# Function to create the database tables
def create_tables():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)

# Function to get a SQLAlchemy session
def get_db():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Define a placeholder list of ticker symbols
ticker_symbols = ["SPX", "SPXW"]

@app.get("/ticker-symbols")
def get_ticker_symbols():
    return ticker_symbols

# request model
class ListOptionsReq(BaseModel):
    tickerSymbol: str
    selectedDate: str
    expireDate: str
    strike: int
    page: int
    perPage: int
# POST request to /list-options
@app.post("/list-options")
async def list_options(option_request: ListOptionsReq, db: Session = Depends(get_db)):
    # print(ticker_symbol, date, perPage,page)
    ticker_symbol = option_request.tickerSymbol
    date = option_request.selectedDate
    expire_date = option_request.expireDate
    strike = option_request.strike
    page = option_request.page
    per_page = option_request.perPage
    # print(strike, expire_date)

    # Calculate the offset based on the page and perPage values
    offset = (page - 1) * per_page
    date_with_dashes = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
    # Query the database for rows that match the ticker symbol and date with pagination
    data_query = (
        select(Option2019)
        .where(Option2019.quotedate == date_with_dashes)
        .where(Option2019.volume > 0)
        .where(Option2019.type == "call")
    )

    total_records_query = (
        select(func.count(Option2019.id))
        .where(Option2019.quotedate == date_with_dashes)
        .where(Option2019.volume > 0)
        .where(Option2019.type == "call")
    )

    if expire_date != "":
        expire_date = datetime.strptime(option_request.expireDate, "%Y-%m-%d").strftime("%Y-%m-%d")
        data_query = data_query.where(Option2019.expiration == expire_date)
        total_records_query = total_records_query.where(Option2019.expiration == expire_date)
    
    if strike != 0:
        data_query = data_query.where(Option2019.strike == strike)
        total_records_query = total_records_query.where(Option2019.strike == strike)

    data_query = data_query.offset(offset).limit(per_page)

    options = db.execute(data_query)
    options = options.scalars().all()
    total_records = db.execute(total_records_query).scalar()
    return {"options": options, "total_records": total_records}

# calculate price request model
class CalPriceRequest(BaseModel):
    ticker: str
    selectedDate: str
    spot: int
    strike: int
    expireDate: str
    r: float
    v: float
@app.post("/calculate-price")
async def calculate_price(req: CalPriceRequest, db: Session = Depends(get_db)):
    strike = req.strike
    selectedDate = datetime.strptime(req.selectedDate, "%Y-%m-%d").date()
    expireDate = datetime.strptime(req.expireDate, "%Y-%m-%d").date()

    r = 0
    v = 0
    spot = 0
    garch_price = 0
    if req.ticker != "":
        r = get_r(req.selectedDate)
        v = get_volatility_ticker(req.ticker, selectedDate)
        spot = get_spot_ticker(req.ticker, selectedDate)
        garch_price = calculate_garch(strike, expireDate, selectedDate, r, req.ticker)
    else:
        r = req.r
        v = req.v
        spot = req.spot
     
     # calculate_bs_2(spot, strike_price, expired_date, current_date, r, vol)
    bs_price = calculate_bs_2(spot, strike, expireDate, selectedDate, r, v)
    mc_price = calculate_mc_2(spot, strike, expireDate, selectedDate, r, v)
    data_query = (
        select(Option2019)
        .where(Option2019.quotedate == selectedDate)
        .where(Option2019.expiration == expireDate)
        .where(Option2019.strike == strike)
        .where(Option2019.volume > 0)
        .where(Option2019.type == "call")
    )
    options = db.execute(data_query).scalars().all()
    market_price = 0 if len(options) == 0 else options[0].last

    res = {
        "bs_price": bs_price,
        "mc_price": mc_price
    }
    if garch_price != 0:
        res["garch_price"] = garch_price
    if market_price != 0:
        res["market_price"] = market_price
    return res

class CalPriceRequest2(BaseModel):
    ticker: str
    selectedDate: str
    strike: int
    expireDate: str
@app.post("/calculate-price-2")
async def calculate_prices(req: CalPriceRequest2, db: Session = Depends(get_db)):
    # response = Response(content_type="text/event-stream")
    # response.headers["Cache-Control"] = "no-cache"
    # response.headers["Connection"] = "keep-alive"

    ticker = req.ticker
    strike = req.strike
    selectedDate = req.selectedDate
    expireDate = req.expireDate

    spot = get_spot(selectedDate)
    r = get_r(selectedDate)
    vol = get_volatility(selectedDate)
    prices_bs = []
    prices_mc = []
    prices_garch = []
    prices_bs_ivolatility = []
    market_prices = []
    strike_prices = []
    expire_dates = []
    if expireDate != "":
        query = (
            select(Option2019)
            .where(Option2019.underlying == ticker)
            .where(Option2019.quotedate == selectedDate)
            .where(Option2019.expiration == expireDate)
            .where(Option2019.volume > 0)
            .where(Option2019.type == "call")
            .order_by(Option2019.strike)
        )
        data = db.execute(query)
        data = data.scalars().all()
        market_prices = [opt.last for opt in data]
        strike_prices = [int(opt.strike) for opt in data]
        expireDate = datetime.strptime(expireDate, "%Y-%m-%d").date()
        for strike_price in strike_prices:
            prices_bs.append(calculate_bs_2(spot, strike_price, expireDate, selectedDate, r, vol))
            prices_mc.append(calculate_mc_2(spot, strike_price, expireDate, selectedDate, r, vol))
            prices_garch.append(calculate_garch(strike_price, expireDate, selectedDate, r))
            bs_ivo, _ = get_d_oprice_values(spot, strike_price, expireDate, selectedDate, r, vol)
            prices_bs_ivolatility.append(bs_ivo)

    else:
        query = (
            select(Option2019)
            .where(Option2019.underlying == ticker)
            .where(Option2019.quotedate == selectedDate)
            .where(Option2019.strike == strike)
            .where(Option2019.volume > 0)
            .where(Option2019.type == "call")
            .order_by(Option2019.expiration)
        )
        data = db.execute(query)
        data = data.scalars().all()
        market_prices = [opt.last for opt in data]
        expire_dates = [opt.expiration for opt in data]
        for expire_date in expire_dates:
            prices_bs.append(calculate_bs_2(spot, strike, expire_date, selectedDate, r, vol))
            prices_mc.append(calculate_mc_2(spot, strike, expire_date, selectedDate, r, vol))
            prices_garch.append(calculate_garch(strike, expire_date, selectedDate, r))
            bs_ivo, _ = get_d_oprice_values(spot, strike, expire_date, selectedDate, r, vol)
            prices_bs_ivolatility.append(bs_ivo)
    
    # plot and save to image
    plt.clf()
    plt.ylabel('Prices')
    plt.title('Comparison of Prices')
    if len(strike_prices) > 0:
        plt.xlabel('Strike Prices')
        plt.plot(strike_prices, market_prices, "-ro", label="Market prices", markersize=2)
        plt.plot(strike_prices, prices_bs, "-go", label="Black-Scholes prices", markersize=2)
        plt.plot(strike_prices, prices_mc, "-bo", label="Monte Carlo prices", markersize=2)
        plt.plot(strike_prices, prices_garch, "-yo", label="GARCH prices", markersize=2)
        plt.plot(strike_prices, prices_bs_ivolatility, "-mo", label="IVolatility prices", markersize=2)
    else:
        plt.xlabel('Expire Date')
        plt.xticks(rotation=90)
        plt.plot(expire_dates, market_prices, "-ro", label="Market prices")
        plt.plot(expire_dates, prices_bs, "-go", label="Black-Scholes prices")
        plt.plot(expire_dates, prices_mc, "-bo", label="Monte Carlo prices")
        plt.plot(expire_dates, prices_garch, "-yo", label="GARCH prices")
        plt.plot(expire_dates, prices_bs_ivolatility, "-mo", label="IVolatility prices")

    plt.legend()

    # Show the plot
    img1_path = "static/foo.png"
    plt.savefig(img1_path)

    plt.clf()
    plt.ylabel('Points')
    plt.title('Comparison of MdAPE points')
    prices_mc = np.array(prices_mc)
    prices_bs = np.array(prices_bs)
    prices_garch = np.array(prices_garch)
    prices_bs_ivolatility = np.array(prices_bs_ivolatility)
    market_prices = np.array([float(p) for p in market_prices])
    mc_mdape = np.abs((prices_mc-market_prices)/market_prices)
    bs_mdape = np.abs((prices_bs-market_prices)/market_prices)
    garch_mdape = np.abs((prices_garch-market_prices)/market_prices)
    ivolatility_mdape = np.abs((prices_bs_ivolatility-market_prices)/market_prices)
    if len(strike_prices) > 0:
        plt.xlabel('Strike Prices')
        plt.plot(strike_prices, bs_mdape, "-go", label="Black-Scholes MdAPE", markersize=2)
        plt.plot(strike_prices, mc_mdape, "-bo", label="Monte Carlo MdAPE", markersize=2)
        plt.plot(strike_prices, garch_mdape, "-yo", label="GARCH MdAPE", markersize=2)
        plt.plot(strike_prices, ivolatility_mdape, "-mo", label="IVolatility MdAPE", markersize=2)
    else:
        plt.xlabel('Expire Date')
        plt.xticks(rotation=90)
        plt.plot(expire_dates, bs_mdape, "-go", label="Black-Scholes MdAPE")
        plt.plot(expire_dates, mc_mdape, "-bo", label="Monte Carlo MdAPE")
        plt.plot(expire_dates, garch_mdape, "-yo", label="GARCH MdAPE")
        plt.plot(expire_dates, ivolatility_mdape, "-mo", label="IVolatility MdAPE")

    plt.legend()
    # Show the plot
    img2_path = "static/bar.png"
    plt.savefig(img2_path)

    return 1


@app.on_event("startup")
async def startup_db():
    await database.connect()

@app.on_event("shutdown")
async def shutdown_db():
    await database.disconnect()

if __name__ == "__main__":
    
    uvicorn.run(
        "main:app",
        host    = "0.0.0.0",
        port    = 8036, 
        reload  = True
    )
    # # Create the tables when the app starts
    # create_tables()