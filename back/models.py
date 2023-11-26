from sqlalchemy import Column, Integer, Date, Time, DECIMAL, \
    String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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
