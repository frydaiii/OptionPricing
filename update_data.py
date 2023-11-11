import yfinance as yf
import datetime

# Define the stock symbol for S&P 500
symbol = "^SPX"

# Set the date range
start_date = "2008-01-01"
end_date = datetime.datetime.now().strftime("%Y-%m-%d")

# Create a ticker object for the S&P 500
spx_ticker = yf.Ticker(symbol)

# Get historical data
historical_data = spx_ticker.history(start=start_date, end=end_date)

# Save the historical data to a CSV file
historical_data.to_csv("spx_historical_data_2008_2020.csv")
