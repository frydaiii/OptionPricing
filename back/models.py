from sqlalchemy import Column, Integer, Date, Time, DECIMAL, \
    String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# _todo remove this
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


class Option2019(Base):
  __tablename__ = 'options_2019'

  id = Column(Integer, primary_key=True, autoincrement=True)
  underlying = Column(String(255))
  underlying_last = Column(Float(precision=10))
  exchange = Column(String(1))
  optionroot = Column(String(255))
  optionext = Column(String(255))
  type = Column(String(10))
  expiration = Column(Date)
  quotedate = Column(Date)
  strike = Column(Float(precision=10))
  last = Column(Float(precision=10))
  bid = Column(Float(precision=10))
  ask = Column(Float(precision=10))
  volume = Column(Integer)
  openinterest = Column(Integer)
  impliedvol = Column(Float(precision=10))
  delta = Column(Float(precision=10))
  gamma = Column(Float(precision=10))
  theta = Column(Float(precision=10))
  vega = Column(Float(precision=10))
  optionalias = Column(String(255))
  IVBid = Column(Float(precision=10))
  IVAsk = Column(Float(precision=10))
