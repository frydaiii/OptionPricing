$(document).ready(function() {
    var optionsPerPage = 10;
    var tickerSymbol;
    var selectedDate;
    var expireDate;
    var strike;
    // Fetch data from the API (assuming it returns an array)
    $.ajax({
        url: '/ticker-symbols', // Replace with your API endpoint
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            // populateDropdown(data, "optionSelect1");
            populateDropdown(data, "optionSelect2");
        },
        error: function(error) {
            console.error('Error fetching data from the API: ' + error.statusText);
        }
    });

    // Function to populate the first dropdown
    function populateDropdown(options, option_select_id) {
        var dropdown = document.getElementById(option_select_id);

        // // Clear any existing options
        // dropdown.innerHTML = "";

        // Iterate through the array and add options to the dropdown
        options.forEach(function(option) {
            var optionElement = document.createElement("option");
            optionElement.value = option; // Assuming the API returns string values
            optionElement.text = option;  // Display the same value as the option text
            dropdown.appendChild(optionElement);
        });
    }

    function getCurrentDate() {
        const today = new Date();
    
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
        const day = String(today.getDate()).padStart(2, '0');
    
        return `${year}-${month}-${day}`;
    }

    // Initialize the datepicker
    // _todo add constraint to datepicker
    $("#expirationDate").datepicker({
        // minDate: getCurrentDate(),
        changeYear: true,
        dateFormat: 'yy-mm-dd'
    });
    year = 2020;
    $("#tradingDate").datepicker({
        minDate: new Date(year, 0, 1),
        maxDate: new Date(year, 11, 31),
        dateFormat: 'yy-mm-dd',
        onSelect: function(date){

        //     var selectedDate = new Date(date);
        //     var msecsInADay = 86400000;
        //     var endDate = new Date(selectedDate.getTime() + msecsInADay);
    
        //    //Set Minimum Date of EndDatePicker After Selected Date of StartDatePicker
        //     $("#expirationDate2").datepicker({
        //         minDate: endDate,
        //         changeYear: true,
        //         dateFormat: 'yy-mm-dd'
        //     });
        //     // $("#endDatePicker").datepicker( "option", "maxDate", '+2y' );
    
        }
    });

    $("#tradingDate2").datepicker({
        minDate: new Date(year, 0, 1),
        maxDate: new Date(year, 11, 31),
        dateFormat: 'yy-mm-dd',
        onSelect: function(date){

            var selectedDate = new Date(date);
            var msecsInADay = 86400000;
            var endDate = new Date(selectedDate.getTime() + msecsInADay);
    
           //Set Minimum Date of EndDatePicker After Selected Date of StartDatePicker
            $("#expirationDate2").datepicker({
                minDate: endDate,
                changeYear: true,
                dateFormat: 'yy-mm-dd'
            });
            // $("#endDatePicker").datepicker( "option", "maxDate", '+2y' );
    
        }
    });

    function calculatePrice(tickerSymbol, selectedDate, spot, strike, expireDate, r, v) {
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
            success: function(response) {
                // Handle the response from the calculation API
                // console.log('Calculation result:', response);
                // Create an image element and set its src attribute
                // var imageElement = $('<img>').attr('src', 'static/foo.png?t=' + new Date().getTime());
                
                // // Append the image to the image container
                // $('#image-container').empty();
                // $('#image-container').append(imageElement);
                // You can display the result or take further actions here
                        // Display the response in a bullet list
                var resultList = $("#result-prices");
                resultList.empty(); // Clear previous results

                $.each(response, function(key, value) {
                    var listItem = $("<li>").text(key + ": " + value);
                    resultList.append(listItem);
                });

                // // Scroll to the results
                // $('html, body').animate({
                //     scrollTop: $("#results").offset().top
                // }, 500);
            },
            error: function(error) {
                console.error('Error calculating price:', error.statusText);
            }
        });
    }

    function calculatePrice2(selectedDate, strike, expireDate) {
        var requestData = {
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
            success: function(response) {
                // Handle the response from the calculation API
                console.log('Calculation result:', response);
                // Create an image element and set its src attribute
                var imageElement = $('<img>').attr('src', 'static/foo.png?t=' + new Date().getTime());
                var imageElement2 = $('<img>').attr('src', 'static/bar.png?t=' + new Date().getTime());
                
                // Append the image to the image container
                $('#image-container-2').empty();
                $('#image-container-2').append(imageElement);
                $('#image-container-2').append(imageElement2);
                // You can display the result or take further actions here
            },
            error: function(error) {
                console.error('Error calculating price:', error.statusText);
            }
        });
    }

    // Handle form submission
    $("#form1").submit(function(event) {
        event.preventDefault(); // Prevent the default form submission
        var optionsList = $("#options-list");
        optionsList.empty(); // Clear existing options
        var paginationControls = $("#pagination-controls");
        paginationControls.empty(); // Clear existing controls

        // Get selected ticker symbol and date from the form
        tickerSymbol = $("#symbolTicker").val();
        selectedDate = $("#tradingDate").val();
        expireDate = $("#expirationDate").val();
        spot = Number($("#spotPrice").val());
        strike = Number($("#strikePrice").val());
        r = parseFloat($("#riskFreeRate").val());
        v = parseFloat($("#volatility").val());

        calculatePrice(tickerSymbol, selectedDate, spot, strike, expireDate, r, v)
    });
    $("#form2").submit(function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Get selected ticker symbol and date from the form
        tickerSymbol = $("#optionSelect2").val();
        selectedDate = $("#tradingDate2").val();
        expireDate = $("#expirationDate2").val();
        strike = Number($("#strikePrice2").val());

        // Make the API request after form submission
        calculatePrice2(selectedDate, strike, expireDate);
    });

    $(".tab-link").on("click", function() {
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
    $("input[name='optionChoice2']").change(function() {
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
    $("input[name='optionChoice']").change(function() {
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
            document.getElementById("tradingDate").value = getCurrentDate();
            // document.getElementsByClassName("rvspotSection").value = 0;
        } else {
            $(".rvspotSection").show();
            $("#tradingDate").show();
            document.getElementById("symbolTicker").required = false;
            document.getElementById("spotPrice").required = true;
            document.getElementById("riskFreeRate").required = true;
            document.getElementById("volatility").required = true;
            document.getElementById("tradingDate").required = true;
            // document.getElementById("spotPrice").value = '';
            // document.getElementById("riskFreeRate").value = '';
            // document.getElementById("volatility").value = '';
            document.getElementById("symbolTicker").value = "";
        }
    });
});
