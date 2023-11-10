from datetime import datetime
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from handle.calculate_prices import handle_calculate_prices
from handle.calculate_price import handle_calculate_price
from handle.calculate_prices_status import handle_calculate_prices_status
from handle.calculate_price_status import handle_calculate_price_status
import uvicorn

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


# calculate price request model
class CalPriceRequest(BaseModel):
  ticker: str
  selectedDate: str  # _todo change to camelcase
  spot: int
  strike: int
  expireDate: str  # _todo change to camelcase
  r: float
  v: float


@app.post("/calculate-price")
async def calculate_price(req: CalPriceRequest, db: Session = Depends(get_db)):
  ticker = req.ticker
  current_date = datetime.strptime(req.selectedDate, "%Y-%m-%d")
  spot = req.spot
  strike = req.strike
  expire_date = datetime.strptime(req.expireDate, "%Y-%m-%d")
  r = req.r
  v = req.v

  return handle_calculate_price(spot, strike, current_date, expire_date, r, v,
                                ticker)


class CalPriceRequestStatus(BaseModel):
  gp_id: str
  garch_id: str
  bs_id: str


@app.post("/calculate-price-status")
async def get_calculate_prices_status(req: CalPriceRequestStatus):
  gp_id = req.gp_id
  garch_id = req.garch_id
  bs_id = req.bs_id

  return handle_calculate_price_status(bs_id, gp_id, garch_id)


class CalPriceRequest2(BaseModel):
  ticker: str
  selectedDate: str  # _todo change to camelcase
  strike: int
  expireDate: str  # _todo change to camelcase


@app.post("/calculate-price-2")
async def calculate_prices(req: CalPriceRequest2,
                           db: Session = Depends(get_db)):

  ticker = req.ticker
  strike = req.strike
  selected_date = datetime.strptime(req.selectedDate, "%Y-%m-%d")
  expire_date = ""
  if req.expireDate != "":
    expire_date = datetime.strptime(req.expireDate, "%Y-%m-%d")

  return handle_calculate_prices(db, strike, selected_date, expire_date,
                                 ticker)


class CalPriceRequest2Status(BaseModel):
  gp_id: str
  garch_id: str
  bs_id: str
  market_id: str


@app.post("/calculate-price-2-status")
async def get_calculate_prices_status(req: CalPriceRequest2Status):
  gp_id = req.gp_id
  garch_id = req.garch_id
  bs_id = req.bs_id
  market_id = req.market_id

  return handle_calculate_prices_status(gp_id, garch_id, bs_id,
                                        market_id)


@app.on_event("startup")
async def startup_db():
  await database.connect()


@app.on_event("shutdown")
async def shutdown_db():
  await database.disconnect()


if __name__ == "__main__":

  uvicorn.run("main:app", host="0.0.0.0", port=8036, reload=True)
  # # Create the tables when the app starts
  # create_tables()
