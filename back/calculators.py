from datetime import timedelta, datetime
import yfinance as yf
import QuantLib as ql
import numpy as np
import math
import arch


def get_r(end_date):
    # get risk free rate, is us treasury bonds in 3 months
    if type(end_date) is str:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    tb_rate = yf.download("^IRX", start=end_date - timedelta(days=3), end=end_date)
    r = tb_rate.iloc[-1]["Close"] or tb_rate.iloc[0]
    return r / 100


def get_volatility_ticker(ticker, date):
    if type(date) is str:
        date = datetime.strptime(date, "%Y-%m-%d")
    # filter
    if ticker == "SPX":
        ticker = "^SPX"
    # create train data is data 10 years before current_date
    end_date = date
    start_date = end_date - timedelta(days=365 * 10)
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    df_close = stock_data["Close"]
    train_data = df_close
    dSprice = np.diff(train_data.to_numpy())
    Sprice = train_data.to_numpy()[:-1]
    volatility = math.sqrt(np.mean(dSprice * dSprice / (Sprice * Sprice * 1 / 365)))
    return volatility


def get_volatility(date):
    return get_volatility_ticker("SPX", date)


def get_spot_ticker(ticker, date):
    if type(date) is str:
        date = datetime.strptime(date, "%Y-%m-%d")
    if ticker == "SPX":
        ticker = "^SPX"
    end_date = date
    start_date = end_date - timedelta(days=3)
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    df_close = stock_data["Close"]
    return df_close.iloc[-1]


def get_spot(date):
    return get_spot_ticker("SPX", date)


def calculate_bs(strike_price, expired_date, current_date):
    # create train data is data 10 years before current_date
    end_date = current_date
    start_date = end_date - timedelta(days=365 * 10)
    stock_data = yf.download("^SPX", start=start_date, end=end_date)
    df_close = stock_data["Close"]
    #   df_log = np.log(df_close)
    train_data = df_close
    dte = (expired_date - train_data.index[-1]).days
    #   volatility = math.sqrt(np.mean(dSprice*dSprice/(Sprice*Sprice*1/365)))
    dSprice = np.diff(train_data.to_numpy())
    Sprice = train_data.to_numpy()[:-1]
    volatility = math.sqrt(np.mean(dSprice * dSprice / (Sprice * Sprice * 1 / 365)))
    #   volatility = iv
    maturity_date = ql.Date(expired_date.day, expired_date.month, expired_date.year)
    spot_price = df_close.iloc[-1]
    dividend_rate = 0
    option_type = ql.Option.Call

    risk_free_rate = get_r(end_date)
    day_count = ql.Actual365Fixed()
    calendar = ql.UnitedStates(ql.UnitedStates.NYSE)

    calculation_date = ql.Date(
        train_data.index[-1].day, train_data.index[-1].month, train_data.index[-1].year
    )
    ql.Settings.instance().evaluationDate = calculation_date

    # construct the European Option
    payoff = ql.PlainVanillaPayoff(option_type, strike_price)
    exercise = ql.EuropeanExercise(maturity_date)
    european_option = ql.VanillaOption(payoff, exercise)

    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
    flat_ts = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, risk_free_rate, day_count)
    )
    dividend_yield = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, dividend_rate, day_count)
    )
    flat_vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)
    )
    bsm_process = ql.BlackScholesMertonProcess(
        spot_handle, dividend_yield, flat_ts, flat_vol_ts
    )

    european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    bs_price = european_option.NPV()
    return bs_price


def calculate_bs_2(spot, strike_price, expired_date, current_date, r, vol):
    if type(expired_date) is str:
        expired_date = datetime.strptime(expired_date, "%Y-%m-%d")
    if type(current_date) is str:
        current_date = datetime.strptime(current_date, "%Y-%m-%d")
    # _todo remove duplicate code
    volatility = vol
    maturity_date = ql.Date(expired_date.day, expired_date.month, expired_date.year)
    spot_price = spot
    dividend_rate = 0
    option_type = ql.Option.Call

    risk_free_rate = r
    day_count = ql.Actual365Fixed()
    calendar = ql.UnitedStates(ql.UnitedStates.NYSE)

    calculation_date = ql.Date(current_date.day, current_date.month, current_date.year)
    ql.Settings.instance().evaluationDate = calculation_date

    # construct the European Option
    payoff = ql.PlainVanillaPayoff(option_type, strike_price)
    exercise = ql.EuropeanExercise(maturity_date)
    european_option = ql.VanillaOption(payoff, exercise)

    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
    flat_ts = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, risk_free_rate, day_count)
    )
    dividend_yield = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, dividend_rate, day_count)
    )
    flat_vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)
    )
    bsm_process = ql.BlackScholesMertonProcess(
        spot_handle, dividend_yield, flat_ts, flat_vol_ts
    )

    european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    bs_price = european_option.NPV()
    return bs_price


def calculate_mc(strike_price, expired_date, current_date):
    # _todo change 365to 252
    # precompute constants
    end_date = current_date
    start_date = end_date - timedelta(days=365 * 10)
    stock_data = yf.download("^SPX", start=start_date, end=end_date)
    df_close = stock_data["Close"]
    train_data = df_close
    dte = (expired_date - df_close.index[-1]).days
    #   volatility = math.sqrt(np.mean(dSprice*dSprice/(Sprice*Sprice*1/365)))
    dSprice = np.diff(train_data.to_numpy())
    Sprice = train_data.to_numpy()[:-1]
    vol = math.sqrt(np.mean(dSprice * dSprice / (Sprice * Sprice * 1 / 365)))
    # vol = iv
    S = df_close.iloc[-1]
    K = strike_price
    M = 100000
    N = 1000
    T = dte / 365
    r = get_r(end_date)

    dt = T / N
    nudt = (r - 0.5 * vol**2) * dt
    volsdt = vol * np.sqrt(dt)
    lnS = np.log(S)
    # Monte Carlo Method
    # _todo this formula could be improved
    Z = np.random.normal(size=(N, M))
    delta_lnSt = nudt + volsdt * Z
    lnSt = lnS + np.cumsum(delta_lnSt, axis=0)
    lnSt = np.concatenate((np.full(shape=(1, M), fill_value=lnS), lnSt))
    # Compute Expectation and SE
    ST = np.exp(lnSt)
    CT = np.maximum(0, ST - K)
    C0 = np.exp(-r * T) * np.sum(CT[-1]) / M
    sigma = np.sqrt(np.sum((CT[-1] - C0) ** 2) / (M - 1))
    SE = sigma / np.sqrt(M)
    return C0


def calculate_mc_2(spot, strike_price, expired_date, current_date, r, vol):
    if type(expired_date) is str:
        expired_date = datetime.strptime(expired_date, "%Y-%m-%d").date()
    if type(current_date) is str:
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

    # _todo remove duplicate code
    dte = (expired_date - current_date).days
    S = spot
    K = strike_price
    M = 1000
    N = 1000
    T = dte / 365

    dt = T / N
    nudt = (r - 0.5 * vol**2) * dt
    volsdt = vol * np.sqrt(dt)
    lnS = np.log(S)
    # Monte Carlo Method
    # _todo this formula could be improved
    Z = np.random.normal(size=(N, M))
    delta_lnSt = nudt + volsdt * Z
    lnSt = lnS + np.cumsum(delta_lnSt, axis=0)
    lnSt = np.concatenate((np.full(shape=(1, M), fill_value=lnS), lnSt))
    # Compute Expectation and SE
    ST = np.exp(lnSt)
    CT = np.maximum(0, ST - K)
    C0 = np.exp(-r * T) * np.sum(CT[-1]) / M
    sigma = np.sqrt(np.sum((CT[-1] - C0) ** 2) / (M - 1))
    SE = sigma / np.sqrt(M)
    return C0

# US average market risk premium
# https://www.statista.com/statistics/664840/average-market-risk-premium-usa/
us_risk_prem = {
    "2011": 0.055,
    "2012": 0.055,
    "2013": 0.057,
    "2014": 0.054,
    "2015": 0.055,
    "2016": 0.053,
    "2017": 0.057,
    "2018": 0.054,
    "2019": 0.056,
    "2020": 0.056,
    "2021": 0.055,
    "2022": 0.056,
    "2023": 0.057,
}
def calculate_garch(strike_price, expire_date, current_date, ticker = ""):
    # expire_date = "2022-12-16"
    if type(expire_date) is str:
        expire_date = datetime.strptime(expire_date, "%Y-%m-%d").date()
    if type(current_date) is str:
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
    if ticker == "SPX" or ticker == "":
        ticker = "^SPX"
    dte = (expire_date - current_date).days
    T = dte / 365

    # get historical data of spx
    end_date = current_date
    start_date = end_date - timedelta(days=365 * 10)
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    df_close = stock_data["Close"]
    df_return = df_close.pct_change().dropna()

    # init and fit model
    model = arch.arch_model(df_return, vol="GARCH", p=1, q=1, rescale=False)
    results = model.fit(disp="off")

    # generate array of annual volatility, include in and out-sample
    lbd = us_risk_prem[str(current_date.year)]  # _todo pls update this
    omega = results.params["omega"]
    alpha = results.params["alpha[1]"]
    beta = results.params["beta[1]"]
    v = results.conditional_volatility
    conditional_var = v**2
    H0 = conditional_var.iloc[-1] / 100
    r = get_r(current_date) / 365

    # monte carlo simulation
    steps = dte
    num_simulations = 1000
    Z = np.random.normal(size=(steps + 1, num_simulations))
    H = np.empty(shape=(steps, num_simulations))
    H = np.concatenate((np.full(shape=(1, num_simulations), fill_value=H0), H))
    lnS = np.empty(shape=(steps, num_simulations))
    lnS = np.concatenate(
        (np.full(shape=(1, num_simulations), fill_value=np.log(df_close.iloc[-1])), lnS)
    )
    for i in range(1, steps + 1):
        # _todo this formula could be improved
        H[i] = omega + (alpha * (Z[i - 1] - lbd) ** 2 + beta) * H[i - 1]
        lnS[i] = lnS[i - 1] + r - 0.5 * H[i] + Z[i] * np.sqrt(H[i])

    paths = np.exp(lnS)
    payoffs = np.maximum(paths[-1] - strike_price, 0)
    option_price = np.mean(payoffs) * np.exp(-r * T)  # discounting back to present value
    return option_price