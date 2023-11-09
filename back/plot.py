from matplotlib import pyplot as plt
import numpy as np

# _todo remove this
def save_img(client_key, prices_bs, prices_mc, prices_garch, 
             prices_bs_ivolatility, prices_gp, market_prices,
             strike_prices = [], expire_dates = []):
    # plot and save to image
    plt.clf()
    plt.ylabel('Prices')
    plt.title('Comparison of Prices')
    if len(strike_prices) > 0:
        plt.xlabel('Strike Prices')
        plt.plot(strike_prices, market_prices, "-ro", label="Market prices", markersize=2)
        plt.plot(strike_prices, prices_bs, "-go", label="Black-Scholes prices", markersize=2)
        plt.plot(strike_prices, prices_mc, "-bo", label="Monte Carlo prices", markersize=2)
        plt.plot(strike_prices, prices_garch, "-yo", label="GARCH prices", markersize=2)
        plt.plot(strike_prices, prices_bs_ivolatility, "-mo", label="IVolatility prices", markersize=2)
        plt.plot(strike_prices, prices_gp, "-ko", label="Gaussian Process prices", markersize=2)
    else:
        plt.xlabel('Expire Date')
        plt.xticks(rotation=90)
        plt.plot(expire_dates, market_prices, "-ro", label="Market prices")
        plt.plot(expire_dates, prices_bs, "-go", label="Black-Scholes prices")
        plt.plot(expire_dates, prices_mc, "-bo", label="Monte Carlo prices")
        plt.plot(expire_dates, prices_garch, "-yo", label="GARCH prices")
        plt.plot(expire_dates, prices_bs_ivolatility, "-mo", label="IVolatility prices")
        plt.plot(expire_dates, prices_gp, "-ko", label="Gaussian Process prices")

    plt.legend()

    # Show the plot
    img1_path = "static/{name}_1.png".format(name=client_key)
    plt.savefig(img1_path)

    plt.clf()
    plt.ylabel('Points')
    plt.title('Comparison of MdAPE points')
    prices_mc = np.array(prices_mc)
    prices_bs = np.array(prices_bs)
    prices_garch = np.array(prices_garch)
    prices_bs_ivolatility = np.array(prices_bs_ivolatility)
    market_prices = np.array([float(p) for p in market_prices])
    mc_mdape = np.abs((prices_mc-market_prices)/market_prices)
    bs_mdape = np.abs((prices_bs-market_prices)/market_prices)
    garch_mdape = np.abs((prices_garch-market_prices)/market_prices)
    ivolatility_mdape = np.abs((prices_bs_ivolatility-market_prices)/market_prices)
    gp_mdape = np.abs((prices_gp-market_prices)/market_prices)
    if len(strike_prices) > 0:
        plt.xlabel('Strike Prices')
        plt.plot(strike_prices, bs_mdape, "-go", label="Black-Scholes MdAPE", markersize=2)
        plt.plot(strike_prices, mc_mdape, "-bo", label="Monte Carlo MdAPE", markersize=2)
        plt.plot(strike_prices, garch_mdape, "-yo", label="GARCH MdAPE", markersize=2)
        plt.plot(strike_prices, ivolatility_mdape, "-mo", label="IVolatility MdAPE", markersize=2)
        plt.plot(strike_prices, gp_mdape, "-ko", label="Gaussian Process MdAPE", markersize=2)
    else:
        plt.xlabel('Expire Date')
        plt.xticks(rotation=90)
        plt.plot(expire_dates, bs_mdape, "-go", label="Black-Scholes MdAPE")
        plt.plot(expire_dates, mc_mdape, "-bo", label="Monte Carlo MdAPE")
        plt.plot(expire_dates, garch_mdape, "-yo", label="GARCH MdAPE")
        plt.plot(expire_dates, ivolatility_mdape, "-mo", label="IVolatility MdAPE")
        plt.plot(expire_dates, gp_mdape, "-ko", label="Gaussian Process MdAPE")

    plt.legend()
    # Show the plot
    img2_path = "static/{name}_2.png".format(name=client_key)
    plt.savefig(img2_path)

    return (img1_path, img2_path)

def save_img_2(id, prices_mc, prices_garch, 
             prices_bs_ivolatility, prices_gp, market_prices,
             strike_prices = [], expire_dates = []):
    # plot and save to image
    plt.clf()
    plt.ylabel('Prices')
    plt.title('Comparison of Prices')
    if len(strike_prices) > 1:
        plt.xlabel('Strike Prices')
        plt.plot(strike_prices, market_prices, "-ro", label="Market prices", markersize=2)
        plt.plot(strike_prices, prices_mc, "-bo", label="Monte Carlo prices", markersize=2)
        plt.plot(strike_prices, prices_garch, "-yo", label="GARCH prices", markersize=2)
        plt.plot(strike_prices, prices_bs_ivolatility, "-mo", label="IVolatility prices", markersize=2)
        plt.plot(strike_prices, prices_gp, "-ko", label="Gaussian Process prices", markersize=2)
    else:
        plt.xlabel('Expire Date')
        plt.xticks(rotation=90)
        plt.plot(expire_dates, market_prices, "-ro", label="Market prices")
        plt.plot(expire_dates, prices_mc, "-bo", label="Monte Carlo prices")
        plt.plot(expire_dates, prices_garch, "-yo", label="GARCH prices")
        plt.plot(expire_dates, prices_bs_ivolatility, "-mo", label="IVolatility prices")
        plt.plot(expire_dates, prices_gp, "-ko", label="Gaussian Process prices")

    plt.legend()

    # Show the plot
    img1_path = "static/{name}_1.png".format(name=id)
    plt.savefig(img1_path)

    plt.clf()
    plt.ylabel('Points')
    plt.title('Comparison of MdAPE points')
    prices_mc = np.array(prices_mc)
    prices_garch = np.array(prices_garch)
    prices_bs_ivolatility = np.array(prices_bs_ivolatility)
    market_prices = np.array([float(p) for p in market_prices])
    mc_mdape = np.abs((prices_mc-market_prices)/market_prices)
    garch_mdape = np.abs((prices_garch-market_prices)/market_prices)
    ivolatility_mdape = np.abs((prices_bs_ivolatility-market_prices)/market_prices)
    gp_mdape = np.abs((prices_gp-market_prices)/market_prices)
    if len(strike_prices) > 1:
        plt.xlabel('Strike Prices')
        plt.plot(strike_prices, mc_mdape, "-bo", label="Monte Carlo MdAPE", markersize=2)
        plt.plot(strike_prices, garch_mdape, "-yo", label="GARCH MdAPE", markersize=2)
        plt.plot(strike_prices, ivolatility_mdape, "-mo", label="IVolatility MdAPE", markersize=2)
        plt.plot(strike_prices, gp_mdape, "-ko", label="Gaussian Process MdAPE", markersize=2)
    else:
        plt.xlabel('Expire Date')
        plt.xticks(rotation=90)
        plt.plot(expire_dates, mc_mdape, "-bo", label="Monte Carlo MdAPE")
        plt.plot(expire_dates, garch_mdape, "-yo", label="GARCH MdAPE")
        plt.plot(expire_dates, ivolatility_mdape, "-mo", label="IVolatility MdAPE")
        plt.plot(expire_dates, gp_mdape, "-ko", label="Gaussian Process MdAPE")

    plt.legend()
    # Show the plot
    img2_path = "static/{name}_2.png".format(name=id)
    plt.savefig(img2_path)

    return (img1_path, img2_path)