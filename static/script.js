import {CalculatePrice, CalculatePrice2} from "./calculate.js"
import {GetCurrentDate} from "./utils.js"

$(document).ready(function () {
  var tickerSymbol;
  var selectedDate;
  var expireDate;
  var strike;
  // Fetch data from the API (assuming it returns an array)
  $.ajax({
    url: '/ticker-symbols', // Replace with your API endpoint
    method: 'GET',
    dataType: 'json',
    success: function (data) {
      // populateDropdown(data, "optionSelect1");
      populateDropdown(data, "optionSelect2");
    },
    error: function (error) {
      console.error('Error fetching data from the API: ' + error.statusText);
    }
  });

  // Function to populate the first dropdown
  function populateDropdown(options, option_select_id) {
    var dropdown = document.getElementById(option_select_id);

    // // Clear any existing options
    // dropdown.innerHTML = "";

    // Iterate through the array and add options to the dropdown
    options.forEach(function (option) {
      var optionElement = document.createElement("option");
      optionElement.value = option; // Assuming the API returns string values
      optionElement.text = option;  // Display the same value as the option text
      dropdown.appendChild(optionElement);
    });
  }

  // Initialize the datepicker
  // _todo add constraint to datepicker
  $("#expirationDate").datepicker({
    // minDate: getCurrentDate(),
    changeYear: true,
    dateFormat: 'yy-mm-dd'
  });
  var year = 2019;
  $("#tradingDate").datepicker({
    minDate: new Date(year, 0, 1),
    maxDate: new Date(year, 11, 31),
    dateFormat: 'yy-mm-dd',
    onSelect: function (date) { }
  });

  $("#tradingDate2").datepicker({
    minDate: new Date(year, 0, 1),
    maxDate: new Date(year, 11, 31),
    dateFormat: 'yy-mm-dd',
    onSelect: function (date) {

      var selectedDate = new Date(date);
      var msecsInADay = 86400000;
      var endDate = new Date(selectedDate.getTime() + msecsInADay);

      //Set Minimum Date of EndDatePicker After Selected Date of StartDatePicker
      $("#expirationDate2").datepicker({
        minDate: endDate,
        changeYear: true,
        dateFormat: 'yy-mm-dd'
      });
    }
  });

  // Handle form submission
  $("#form1").submit(function (event) {
    event.preventDefault(); // Prevent the default form submission
    $('#result-prices').empty();

    // Get selected ticker symbol and date from the form
    var type=$("input[name='type']:checked").val()
    tickerSymbol = $("#symbolTicker").val();
    selectedDate = $("#tradingDate").val();
    expireDate = $("#expirationDate").val();
    var spot = Number($("#spotPrice").val());
    strike = Number($("#strikePrice").val());
    var r = parseFloat($("#riskFreeRate").val());
    var v = parseFloat($("#volatility").val());

    CalculatePrice(type, tickerSymbol, selectedDate, spot, strike, expireDate, r, v)
  });
  $("#form2").submit(function (event) {
    event.preventDefault(); // Prevent the default form submission
    $('#image-container-2').empty();

    // Get selected ticker symbol and date from the form
    var type=$("input[name='type']:checked").val()
    tickerSymbol = $("#optionSelect2").val();
    selectedDate = $("#tradingDate2").val();
    expireDate = $("#expirationDate2").val();
    strike = Number($("#strikePrice2").val());

    // Make the API request after form submission
    CalculatePrice2(type, tickerSymbol, selectedDate, strike, expireDate);
  });

  $(".tab-link").on("click", function () {
    var tabId = $(this).data("tab");
    $(".tab-link").removeClass("current");
    $(".tab-content").removeClass("current");
    $(this).addClass("current");
    $("#" + tabId).addClass("current");
  });

  // Initially, hide both input sections
  $("#strikePriceSection").hide();
  $("#expirationDateSection").hide();

  // Listen for changes to the radio buttons
  $("input[name='optionChoice2']").change(function () {
    var selectedOption = $(this).val();

    // Hide both sections
    $("#strikePriceSection").hide();
    $("#expirationDateSection").hide();

    // Show the selected section
    if (selectedOption === "strikePrice") {
      $("#strikePriceSection").show();
      document.getElementById("strikePrice2").required = true;
      document.getElementById("expirationDate2").required = false;
      document.getElementById("expirationDate2").value = "";
    } else if (selectedOption === "expirationDate") {
      $("#expirationDateSection").show();
      document.getElementById("strikePrice2").required = false;
      document.getElementById("expirationDate2").required = true;
      document.getElementById("strikePrice2").value = "";
    }
  });

  $("#symbolTickerSection").hide();
  $(".rvspotSection").hide();

  // Listen for changes to the radio buttons
  $("input[name='optionChoice']").change(function () {
    // Get the selected option
    var selectedOption = $("input[name='optionChoice']:checked").val();

    // Hide both sections
    $("#symbolTickerSection").hide();
    $("#tradingDate").hide();
    $(".rvspotSection").hide();

    // Show the selected section
    if (selectedOption === "calToday") {
      $("#symbolTickerSection").show();
      document.getElementById("symbolTicker").required = true;
      document.getElementById("spotPrice").required = false;
      document.getElementById("riskFreeRate").required = false;
      document.getElementById("volatility").required = false;
      document.getElementById("tradingDate").required = false;
      document.getElementById("spotPrice").value = 0;
      document.getElementById("riskFreeRate").value = 0;
      document.getElementById("volatility").value = 0;
      document.getElementById("tradingDate").value = GetCurrentDate();
    } else {
      $(".rvspotSection").show();
      $("#tradingDate").show();
      document.getElementById("symbolTicker").required = false;
      document.getElementById("spotPrice").required = true;
      document.getElementById("riskFreeRate").required = true;
      document.getElementById("volatility").required = true;
      document.getElementById("tradingDate").required = true;
      document.getElementById("symbolTicker").value = "";
    }
  });
});
