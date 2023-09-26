from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, DECIMAL, MetaData, func, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
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