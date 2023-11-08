from datetime import timedelta, datetime
import yfinance as yf
import QuantLib as ql
import numpy as np
import math
import arch
import requests
from bs4 import BeautifulSoup
import re
from back.utils import *
from back.garch import garch_1_1
from statistics import variance

def calculate_bs(strike_price, expired_date, current_date):
    # create train data is data 10 years before current_date
    end_date = current_date
    start_date = end_date - timedelta(days=365 * 10)

    stock_data = get_data(start_date, end_date)
       
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
    # _todo wrapper this
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
    stock_data = get_data(start_date, end_date)
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
def calculate_garch(strike_prices: [], expire_dates: [], current_date, r, ticker = ""):
    # expire_date = "2022-12-16"
    for i in range(0, len(expire_dates)):
        if type(expire_dates[i]) is str:
            expire_dates[i] = datetime.strptime(expire_dates[i], "%Y-%m-%d").date()
    if type(current_date) is str:
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
    if ticker == "SPX" or ticker == "":
        ticker = "^SPX"

    # get historical data of spx
    end_date = current_date
    start_date = end_date - timedelta(days=365 * 10)

    stock_data = get_data(start_date, end_date, ticker)
       
    df_close = stock_data["Close"]
    df_return = df_close.pct_change().dropna()

    # init and fit model
    daily_r = r / 360 # the input param is risk free rate in a year
    lbd = us_risk_prem[str(current_date.year)]  # _todo pls update this
    model = garch_1_1(df_return.to_numpy(), daily_r, lbd)
    model.optimize()

    # generate array of annual volatility, include in and out-sample
    omega = model.params[0]
    alpha = model.params[1]
    beta = model.params[2]
    H0 = variance(df_return)

    # monte carlo simulation
    option_prices = []
    assert ((len(strike_prices) == 1 and len(expire_dates) == 1) # single option
        or (len(strike_prices) == 1 and len(expire_dates) > 1) # multiple options
        or (len(strike_prices) > 1 and len(expire_dates) == 1)) # multiple options
    for strike_price in strike_prices:
        for expire_date in expire_dates:
            dte = (expire_date - current_date).days
            T = dte / 365
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
                lnS[i] = lnS[i - 1] + daily_r - 0.5 * H[i] + Z[i] * np.sqrt(H[i])

            paths = np.exp(lnS)
            payoffs = np.maximum(paths[-1] - strike_price, 0)
            option_price = np.mean(payoffs) * np.exp(-r * T)  # discounting back to present value
            option_prices.append(option_price)
    return option_prices

'''
The following function call to ivolatility.com and extract the option price from
response. The response should look like this:
    <html>
    <head>
    <script language="JavaScript"><!--
    function go() {
    var d =  parent.calc.document.grek;
    if (d!=null) {
    d.oprice_c.value='1000.0031';
    d.oprice_p.value='0.0000';
    d.delta_c.value='1.0000';
    d.delta_p.value='0.0000';
    d.gamma_c.value='0.0000';
    d.gamma_p.value='0.0000';
    d.theta_c.value='-0.0031';
    d.theta_p.value='0.0000';
    d.vega_c.value='0.0000';
    d.vega_p.value='0.0000';
    d.rho_c.value='0.0030';
    d.rho_p.value='0.0000';
    }
    }
    //--></script>
    </head>
    <body onload="go()">
    </body>
    </html>
'''
def get_d_oprice_values(spot, strike, expired_date, current_date, r, vol):
    if type(expired_date) is str:
        expired_date = datetime.strptime(expired_date, "%Y-%m-%d").date()
    if type(current_date) is str:
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

    # _todo remove duplicate code
    dte = (expired_date - current_date).days
    url = generate_option_calculation_url(dte, vol, r, spot, strike)
    # Send a GET request to the URL and store the response
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print("Request failed with status code:", response.status_code)
        return None

    # Parse the HTML content of the response using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Use a regular expression to find and extract the values of d.oprice_c.value and d.oprice_p.value
    script_content = soup.find('script').string
    d_oprice_c_match = re.search(r"d.oprice_c.value='([^']*)'", script_content)
    d_oprice_p_match = re.search(r"d.oprice_p.value='([^']*)'", script_content)

    if d_oprice_c_match and d_oprice_p_match:
        d_oprice_c_value = d_oprice_c_match.group(1)
        d_oprice_p_value = d_oprice_p_match.group(1)
        return float(d_oprice_c_value), float(d_oprice_p_value)
    else:
        print("One or both values not found")
        return None, None
    
def generate_option_calculation_url(daysexp, vola, intrate, price, strike):
    # _todo pls note that jsessionid could change when time varying
    base_url = "https://oic.ivolatility.com/calc/calc_logic.j;jsessionid=bTEB1L1i1P55?"
    
    # Define the parameters
    params = {
        "is_stock": "0",
        "SID": "",
        "currency": "",
        "rid": "0",
        "A": "0",
        "days": "",
        "country": "E",
        "daysexp": daysexp,
        "vola": vola,
        "intrate": intrate,
        "price": price,
        "strike": strike,
        "opt_price": "",
        "tp": "",
        "freq": "12",
        "divlastdate": "",
        "divyield": ""
    }
    
    # Create the parameter string
    param_string = "&".join([f"{key}={value}" for key, value in params.items()])
    
    # Combine the base URL and parameter string to form the complete URL
    complete_url = base_url + param_string
    
    return complete_url