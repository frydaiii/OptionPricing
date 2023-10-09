import QuantLib as ql
import yfinance as yf
import numpy as np
import math
from datetime import datetime, timedelta
def get_r(end_date):
  # get risk free rate, is us treasury bonds in 3 months
  tb_rate = yf.download("^IRX", start=end_date - timedelta(days=2), end=end_date)
  r = tb_rate.iloc[-1]["Close"]
  return r
def calculate_bs(strike_price, expired_date, current_date, iv):
  # create train data is data 10 years before current_date
  end_date = current_date
  start_date = end_date - timedelta(days=365 * 10)
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

def calculate_mc(strike_price, expired_date, current_date):
    #precompute constants
    end_date = current_date
    start_date = end_date - timedelta(days=365*10)
    stock_data = yf.download("^SPX", start=start_date, end=end_date)
    df_close = stock_data['Close']
    train_data = df_close
    dte = (expired_date - df_close.index[-1]).days
    #   volatility = math.sqrt(np.mean(dSprice*dSprice/(Sprice*Sprice*1/365)))
    dSprice = np.diff(train_data.to_numpy())
    Sprice = train_data.to_numpy()[:-1] 
    vol = math.sqrt(np.mean(dSprice*dSprice/(Sprice*Sprice*1/365)))
    # vol = iv
    S = df_close.iloc[-1]
    K = strike_price
    M = 5000
    N = 100
    T = dte/365
    r = 0.0015

    print("Spot: " + str(S) + " strike: " + str(K) + " dte: " + str(dte) + 
          " volatility: " + str(vol) + " r: " + str(r))

    # dt = T/N
    # nudt = (r - 0.5*vol**2)*dt
    # volsdt = vol*np.sqrt(dt)
    # lnS = np.log(S)
    # # Monte Carlo Method
    # Z = np.random.normal(size=(N, M))
    # delta_lnSt = nudt + volsdt*Z
    # lnSt = lnS + np.cumsum(delta_lnSt, axis=0)
    # lnSt = np.concatenate( (np.full(shape=(1, M), fill_value=lnS), lnSt ) )
    # # Compute Expectation and SE
    # ST = np.exp(lnSt)
    # CT = np.maximum(0, ST - K)
    # for s in ST:
    #    print(s)
    # C0 = np.exp(-r*T)*np.sum(CT[-1])/M
    # sigma = np.sqrt( np.sum( (CT[-1] - C0)**2) / (M-1) )
    # SE = sigma/np.sqrt(M)
    #precompute constants
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
    print("Call value is ${0} with SE +/- {1}".format(np.round(C0,2),np.round(SE,2)))
    return C0

strike = 3275
selectedDate = datetime.strptime("01/02/2020", "%m/%d/%Y")
expireDate = datetime.strptime("2020-03-31", "%Y-%m-%d")
# print(calculate_mc(strike, expireDate, selectedDate))
print(get_r(selectedDate))


def geo_paths(S, T, r, q, sigma, steps, N):
    """
    Inputs
    #S = Current stock Price
    #K = Strike Price
    #T = Time to maturity 1 year = 1, 1 months = 1/12
    #r = risk free interest rate
    #q = dividend yield
    # sigma = volatility 
    
    Output
    # [steps,N] Matrix of asset paths 
    """
    dt = T/steps
    #S_{T} = ln(S_{0})+\int_{0}^T(\mu-\frac{\sigma^2}{2})dt+\int_{0}^T \sigma dW(t)
    ST = np.log(S) +  np.cumsum(((r - q - sigma**2/2)*dt +\
                              sigma*np.sqrt(dt) * \
                              np.random.normal(size=(steps,N))),axis=0)
    
    return np.exp(ST)

S = 3230 #stock price S_{0}
K = 3275 # strike
T = 0.25 # time to maturity
r = 0.015 # risk free risk in annual %
q = 0 # annual dividend rate
sigma = 0.178 # annual volatility in %
steps = 100 # time steps
N = 1000 # number of trials

paths= geo_paths(S,T,r, q,sigma,steps,N)
payoffs = np.maximum(paths[-1]-K, 0)
option_price = np.mean(payoffs)*np.exp(-r*T) #discounting back to present value

print(option_price)