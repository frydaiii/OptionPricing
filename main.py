from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, DECIMAL, MetaData, func, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import yfinance as yf
import QuantLib as ql
import numpy as np
import math
import uvicorn

# Define database URL
DATABASE_URL = "mysql+pymysql://root:1@localhost:3306/option_chains"

# Create a database instance
database = Database(DATABASE_URL)

# Define your SQLAlchemy models if needed
Base = declarative_base()


class OptionData(Base):
    __tablename__ = "options_data"
    id = Column(Integer, primary_key=True, index=True)
    quote_unixtime = Column(Integer)
    quote_readtime = Column(Date)
    quote_date = Column(Date)
    quote_time_hours = Column(Time)
    underlying_last = Column(DECIMAL(10, 2))
    expire_date = Column(Date)
    expire_unix = Column(Integer)
    dte = Column(Integer)
    c_delta = Column(DECIMAL(10, 2))
    c_gamma = Column(DECIMAL(10, 2))
    c_vega = Column(DECIMAL(10, 2))
    c_theta = Column(DECIMAL(10, 2))
    c_rho = Column(DECIMAL(10, 2))
    c_iv = Column(DECIMAL(10, 2))
    c_volume = Column(DECIMAL(10, 2))
    c_last = Column(DECIMAL(10, 2))
    c_size = Column(Integer)
    c_bid = Column(DECIMAL(10, 2))
    c_ask = Column(DECIMAL(10, 2))
    strike = Column(DECIMAL(10, 2))
    p_bid = Column(DECIMAL(10, 2))
    p_ask = Column(DECIMAL(10, 2))
    p_size = Column(Integer)
    p_last = Column(DECIMAL(10, 2))
    p_delta = Column(DECIMAL(10, 2))
    p_gamma = Column(DECIMAL(10, 2))
    p_vega = Column(DECIMAL(10, 2))
    p_theta = Column(DECIMAL(10, 2))
    p_rho = Column(DECIMAL(10, 2))
    p_iv = Column(DECIMAL(10, 2))
    p_volume = Column(Integer)
    strike_distance = Column(DECIMAL(10, 2))
    strike_distance_pct = Column(DECIMAL(10, 2))

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
    page: int
    perPage: int
# POST request to /list-options
@app.post("/list-options")
async def list_options(option_request: ListOptionsReq, db: Session = Depends(get_db)):
    # print(ticker_symbol, date, perPage,page)
    ticker_symbol = option_request.tickerSymbol
    date = option_request.selectedDate
    page = option_request.page
    per_page = option_request.perPage

    # Calculate the offset based on the page and perPage values
    offset = (page - 1) * per_page
    date_with_dashes = datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
    # Query the database for rows that match the ticker symbol and date with pagination
    query = (
        select(OptionData)
        .where(OptionData.quote_date == date_with_dashes)
        .where(OptionData.c_volume > 0)
        # .where(or_(OptionData.c_symbol == ticker_symbol, OptionData.p_symbol == ticker_symbol))
        .offset(offset)
        .limit(per_page)
    )

    options = db.execute(query)
    options = options.scalars().all()
    return options

# calculate price request model
class CalPriceRequest(BaseModel):
    selectedDate: str
    strike: float
    expireDate: str
    volatility: float
@app.post("/calculate-price")
async def list_options(req: CalPriceRequest):
    strike = req.strike
    selectedDate = datetime.strptime(req.selectedDate, "%m/%d/%Y")
    expireDate = datetime.strptime(req.expireDate, "%Y-%m-%d")
    volatility = req.volatility
    
    return str(calculate_bs(strike, expireDate, selectedDate, volatility)) + " " + str(calculate_mc(strike, expireDate, selectedDate, volatility))

@app.on_event("startup")
async def startup_db():
    await database.connect()

@app.on_event("shutdown")
async def shutdown_db():
    await database.disconnect()

def get_r(end_date):
  # get risk free rate, is us treasury bonds in 3 months
  tb_rate = yf.download("^IRX", start=end_date - timedelta(days=2), end=end_date)
  r = tb_rate.iloc[-1]["Close"]
  return r
def calculate_bs(strike_price, expired_date, current_date, iv):
  # create train data is data 10 years before current_date
  end_date = current_date
  start_date = end_date - timedelta(days=2)
  stock_data = yf.download("^SPX", start=start_date, end=end_date)
  df_close = stock_data['Close']
#   df_log = np.log(df_close)
  train_data = df_close
  dte = (expired_date - train_data.index[-1]).days
#   volatility = math.sqrt(np.mean(dSprice*dSprice/(Sprice*Sprice*1/365)))
  volatility = iv
  maturity_date = ql.Date(expired_date.day, expired_date.month, expired_date.year)
  spot_price = df_close.iloc[-1]
  dividend_rate =  0
  option_type = ql.Option.Call

  risk_free_rate = get_r(end_date)
  day_count = ql.Actual365Fixed()
  calendar = ql.UnitedStates(ql.UnitedStates.NYSE)

  calculation_date = ql.Date(train_data.index[-1].day, train_data.index[-1].month, train_data.index[-1].year)
  ql.Settings.instance().evaluationDate = calculation_date

  # construct the European Option
  payoff = ql.PlainVanillaPayoff(option_type, strike_price)
  exercise = ql.EuropeanExercise(maturity_date)
  european_option = ql.VanillaOption(payoff, exercise)

  spot_handle = ql.QuoteHandle(
      ql.SimpleQuote(spot_price)
  )
  flat_ts = ql.YieldTermStructureHandle(
      ql.FlatForward(calculation_date, risk_free_rate, day_count)
  )
  dividend_yield = ql.YieldTermStructureHandle(
      ql.FlatForward(calculation_date, dividend_rate, day_count)
  )
  flat_vol_ts = ql.BlackVolTermStructureHandle(
      ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)
  )
  bsm_process = ql.BlackScholesMertonProcess(spot_handle,
                                            dividend_yield,
                                            flat_ts,
                                            flat_vol_ts)

  european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
  bs_price = european_option.NPV()
  return bs_price

def calculate_mc(strike_price, expired_date, current_date, iv):
    #precompute constants
    end_date = current_date
    start_date = end_date - timedelta(days=2)
    stock_data = yf.download("^SPX", start=start_date, end=end_date)
    df_close = stock_data['Close']
    dte = (expired_date - df_close.index[-1]).days
    #   volatility = math.sqrt(np.mean(dSprice*dSprice/(Sprice*Sprice*1/365)))
    vol = iv
    S = df_close.iloc[-1]
    K = strike_price
    M = 100000
    N = 1
    T = dte/365
    r = get_r(end_date)

    dt = T/N
    nudt = (r - 0.5*vol**2)*dt
    volsdt = vol*np.sqrt(dt)
    lnS = np.log(S)
    # Monte Carlo Method
    Z = np.random.normal(size=(N, M))
    delta_lnSt = nudt + volsdt*Z
    lnSt = lnS + np.cumsum(delta_lnSt, axis=0)
    lnSt = np.concatenate( (np.full(shape=(1, M), fill_value=lnS), lnSt ) )
    # Compute Expectation and SE
    ST = np.exp(lnSt)
    CT = np.maximum(0, ST - K)
    C0 = np.exp(-r*T)*np.sum(CT[-1])/M
    sigma = np.sqrt( np.sum( (CT[-1] - C0)**2) / (M-1) )
    SE = sigma/np.sqrt(M)
    return C0

if __name__ == "__main__":
    
    uvicorn.run(
        "main:app",
        host    = "0.0.0.0",
        port    = 8036, 
        reload  = True
    )
    # # Create the tables when the app starts
    # create_tables()