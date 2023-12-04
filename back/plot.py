from matplotlib import pyplot as plt
import numpy as np


def save_img(id,
             prices_garch,
             prices_bs,
             prices_gp,
             market_prices,
             strike_prices=[],
             spot_prices=[],
             expire_dates=[]):
  # plot and save to image
  plt.clf()
  # plt.ylabel('Prices')
  # plt.title('So sánh giá')
  if len(strike_prices) > 1:
    plt.xlabel('K/S')
    plt.plot(np.array(strike_prices)/np.array(spot_prices),
             market_prices,
             "-ro",
             label="Giá thị trường",
             markersize=2)
    plt.plot(np.array(strike_prices)/np.array(spot_prices),
             prices_garch,
             "-yo",
             label="GARCH",
             markersize=2)
    plt.plot(np.array(strike_prices)/np.array(spot_prices),
             prices_bs,
             "-mo",
             label="Black Scholes",
             markersize=2)
    plt.plot(np.array(strike_prices)/np.array(spot_prices),
             prices_gp,
             "-ko",
             label="Quá trình Gauss",
             markersize=2)
  else:
    plt.xlabel('Ngày đáo hạn')
    plt.xticks(rotation=90)
    plt.plot(expire_dates, market_prices, "-ro", label="Giá thị trường")
    plt.plot(expire_dates, prices_garch, "-yo", label="GARCH")
    plt.plot(expire_dates, prices_bs, "-mo", label="Black Scholes")
    plt.plot(expire_dates, prices_gp, "-ko", label="Quá trình Gauss")

  plt.legend()

  # Show the plot
  img1_path = "static/{name}_1.png".format(name=id)
  plt.savefig(img1_path)

  plt.clf()
  # plt.ylabel('Points')
  # plt.title('So sánh sai số')
  prices_garch = np.array(prices_garch)
  prices_bs = np.array(prices_bs)
  market_prices = np.array([float(p) for p in market_prices])
  garch_mape = np.abs((prices_garch - market_prices) / market_prices)
  bs_mape = np.abs((prices_bs - market_prices) / market_prices)
  gp_mape = np.abs((prices_gp - market_prices) / market_prices)
  if len(strike_prices) > 1:
    plt.xlabel('K/S')
    plt.plot(np.array(strike_prices)/np.array(spot_prices),
             garch_mape,
             "-yo",
             label="GARCH",
             markersize=2)
    plt.plot(np.array(strike_prices)/np.array(spot_prices),
             bs_mape,
             "-mo",
             label="Black Scholes",
             markersize=2)
    plt.plot(np.array(strike_prices)/np.array(spot_prices),
             gp_mape,
             "-ko",
             label="Quá trình Gauss",
             markersize=2)
  else:
    plt.xlabel('Ngày đáo hạn')
    plt.xticks(rotation=90)
    plt.plot(expire_dates, garch_mape, "-yo", label="GARCH")
    plt.plot(expire_dates, bs_mape, "-mo", label="Black Scholes")
    plt.plot(expire_dates, gp_mape, "-ko", label="Quá trình Gauss")

  plt.legend()
  # Show the plot
  img2_path = "static/{name}_2.png".format(name=id)
  plt.savefig(img2_path)

  return (img1_path, img2_path)
