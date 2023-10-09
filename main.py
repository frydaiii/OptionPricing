from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from databases import Database
from matplotlib import pyplot as plt
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, DECIMAL, MetaData, func, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
from back.models import OptionData
from back.calculators import calculate_bs, calculate_mc, \
    calculate_bs_2, calculate_mc_2, get_r, get_spot, \
        get_volatility, get_volatility_ticker, get_spot_ticker
import yfinance as yf
import QuantLib as ql
import numpy as np
import math
import uvicorn
import os

# Define database URL
DATABASE_URL = "mysql+pymysql://manh:1@localhost:3306/option_chains"

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
ticker_symbols = ["SPX"]

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
        select(OptionData)
        .where(OptionData.quote_date == date_with_dashes)
        .where(OptionData.c_volume > 0)
    )

    total_records_query = (
        select(func.count(OptionData.id))
        .where(OptionData.quote_date == date_with_dashes)
        .where(OptionData.c_volume > 0)
    )

    if expire_date != "":
        expire_date = datetime.strptime(option_request.expireDate, "%Y-%m-%d").strftime("%Y-%m-%d")
        data_query = data_query.where(OptionData.expire_date == expire_date)
        total_records_query = total_records_query.where(OptionData.expire_date == expire_date)
    
    if strike != 0:
        data_query = data_query.where(OptionData.strike == strike)
        total_records_query = total_records_query.where(OptionData.strike == strike)

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
    if req.ticker != "":
        r = get_r(req.selectedDate)
        v = get_volatility_ticker(req.ticker, selectedDate)
        spot = get_spot_ticker(req.ticker, selectedDate)
    else:
        r = req.r
        v = req.v
        spot = req.spot
     
     # calculate_bs_2(spot, strike_price, expired_date, current_date, r, vol)
    bs_price = calculate_bs_2(spot, strike, expireDate, selectedDate, r, v)
    mc_price = calculate_mc_2(spot, strike, expireDate, selectedDate, r, v)
    data_query = (
        select(OptionData)
        .where(OptionData.quote_date == selectedDate)
        .where(OptionData.expire_date == expireDate)
        .where(OptionData.strike == strike)
        .where(OptionData.c_volume > 0)
    )
    options = db.execute(data_query).scalars().all()
    market_price = 0 if len(options) == 0 else options[0].c_last

    # # print to image
    # bar_width = 0.2

    # # Create the bar chart
    # plt.clf()
    # plt.bar(0, mc_price, width=bar_width, label='MC Prices', align='center')
    # plt.bar(bar_width, bs_price, width=bar_width, label='BS Prices', align='center')
    # plt.bar(2*bar_width, market_price, width=bar_width, label='Market Prices', align='center')

    # # Customize the chart
    # plt.ylabel('Prices')
    # plt.title('Comparison of Prices')
    # plt.legend()

    # # Show the plot
    # img_path = "static/foo.png"
    # plt.savefig(img_path)

    res = {
        "bs_price": bs_price,
        "mc_price": mc_price,
        "market_price": market_price
    }
    return res


@app.post("/calculate-price-2")
async def calculate_prices(req: CalPriceRequest, db: Session = Depends(get_db)):
    strike = req.strike
    selectedDate = req.selectedDate
    expireDate = req.expireDate

    spot = get_spot(selectedDate)
    r = get_r(selectedDate)
    vol = get_volatility(selectedDate)
    prices_bs = []
    prices_mc = []
    market_prices = []
    strike_prices = []
    expire_dates = []
    if expireDate != "":
        query = (
            select(OptionData)
            .where(OptionData.quote_date == selectedDate)
            .where(OptionData.expire_date == expireDate)
            .where(OptionData.c_volume > 0)
            .order_by(OptionData.strike)
        )
        data = db.execute(query)
        data = data.scalars().all()
        market_prices = [opt.c_last for opt in data]
        strike_prices = [int(opt.strike) for opt in data]
        expireDate = datetime.strptime(expireDate, "%Y-%m-%d").date()
        for strike_price in strike_prices:
            prices_bs.append(calculate_bs_2(spot, strike_price, expireDate, selectedDate, r, vol))
            prices_mc.append(calculate_mc_2(spot, strike_price, expireDate, selectedDate, r, vol))

    else:
        query = (
            select(OptionData)
            .where(OptionData.quote_date == selectedDate)
            .where(OptionData.strike == strike)
            .where(OptionData.c_volume > 0)
            .order_by(OptionData.expire_date)
        )
        data = db.execute(query)
        data = data.scalars().all()
        market_prices = [opt.c_last for opt in data]
        expire_dates = [opt.expire_date for opt in data]
        for expire_date in expire_dates:
            prices_bs.append(calculate_bs_2(spot, strike, expire_date, selectedDate, r, vol))
            prices_mc.append(calculate_mc_2(spot, strike, expire_date, selectedDate, r, vol))
    
    # plot and save to image
    plt.ylabel('Prices')
    plt.title('Comparison of Prices')
    if len(strike_prices) > 0:
        plt.clf()
        plt.xlabel('Strike Prices')
        plt.plot(strike_prices, market_prices, "-ro", label="Market prices", markersize=2)
        plt.plot(strike_prices, prices_bs, "-go", label="Black-Scholes prices", markersize=2)
        plt.plot(strike_prices, prices_mc, "-bo", label="Monte Carlo prices", markersize=2)
    else:
        plt.clf()
        plt.xlabel('Expire Date')
        plt.plot(expire_dates, market_prices, "-ro", label="Market prices")
        plt.plot(expire_dates, prices_bs, "-go", label="Black-Scholes prices")
        plt.plot(expire_dates, prices_mc, "-bo", label="Monte Carlo prices")

    plt.legend()

    # Show the plot
    img_path = "static/bar.png"
    plt.savefig(img_path)

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