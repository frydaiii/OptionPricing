from datetime import datetime
from fastapi import FastAPI, Request, Depends, Response, BackgroundTasks
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
from handle.calculate_prices import handle_calculate_prices
from handle.calculate_prices_status import handle_calculate_prices_status
import uvicorn
from back.cache import pricing
from worker.main import rd

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
        garch_price = calculate_garch([strike], [expireDate], selectedDate, r, req.ticker)[0]
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
    if req.ticker != "":
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
async def calculate_prices(req: CalPriceRequest2, 
    db: Session = Depends(get_db)):

    ticker = req.ticker
    strike = req.strike
    selected_date = req.selectedDate
    expire_date = req.expireDate

    return handle_calculate_prices(db, strike, selected_date, expire_date, ticker)

class CalPriceRequest2Status(BaseModel):
    gp_id: str
    garch_id: str
    mc_id: str
    bs_ivo_id: str
    market_id: str
@app.post("/calculate-price-2-status")
async def get_calculate_prices_status(req: CalPriceRequest2Status):
    gp_id = req.gp_id
    garch_id = req.garch_id
    mc_id = req.mc_id
    bs_ivo_id = req.bs_ivo_id
    market_id = req.market_id

    return handle_calculate_prices_status(gp_id, garch_id, mc_id, bs_ivo_id, market_id)
    

@app.on_event("startup")
async def startup_db():
    await database.connect()

@app.on_event("shutdown")
async def shutdown_db():
    await database.disconnect()

@app.on_event("shutdown")
async def clear_cache():
    pricing.close()

if __name__ == "__main__":
    
    uvicorn.run(
        "main:app",
        host    = "0.0.0.0",
        port    = 8036, 
        reload  = True
    )
    # # Create the tables when the app starts
    # create_tables()