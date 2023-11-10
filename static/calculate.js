import {UpdateCalculatePrice2Result, UpdateCalculatePriceResult} from "./update.js"

function CalculatePrice(tickerSymbol, selectedDate, spot, strike, expireDate, r, v) {
  var requestData = {
    ticker: tickerSymbol,
    selectedDate: selectedDate,
    spot: spot,
    strike: strike,
    expireDate: expireDate,
    r: r,
    v: v
  };

  $.ajax({
    url: '/calculate-price',
    method: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(requestData),
    success: function (response) {
      UpdateCalculatePriceResult(response);
    },
    error: function (error) {
      console.error('Error calculating price:', error.statusText);
    }
  });
}

function CalculatePrice2(ticker, selectedDate, strike, expireDate) {
  var requestData = {
    ticker: ticker,
    selectedDate: selectedDate,
    strike: strike,
    expireDate: expireDate
  };

  $.ajax({
    url: '/calculate-price-2',
    method: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(requestData),
    success: function (response) {
      // Handle the response from the calculation API
      console.log('Calculation result:', response);
      UpdateCalculatePrice2Result(response);
    },
    error: function (error) {
      console.error('Error calculating price:', error.statusText);
    }
  });
}

export {CalculatePrice, CalculatePrice2}