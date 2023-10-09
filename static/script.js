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

    // Initialize the datepicker
    year = 2020;
    $("#tradingDate").datepicker({
        minDate: new Date(year, 0, 1),
        maxDate: new Date(year, 11, 31),
        dateFormat: 'yy-mm-dd',
        onSelect: function(date){

            var selectedDate = new Date(date);
            var msecsInADay = 86400000;
            var endDate = new Date(selectedDate.getTime() + msecsInADay);
    
           //Set Minimum Date of EndDatePicker After Selected Date of StartDatePicker
            $("#expirationDate").datepicker({
                minDate: endDate,
                changeYear: true,
                dateFormat: 'yy-mm-dd'
            });
            // $("#endDatePicker").datepicker( "option", "maxDate", '+2y' );
    
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

    // $("#expirationDate").datepicker({
    //     changeYear: true
    // });


    // // Function to fetch options from the API and display them
    // function fetchAndDisplayOptions(pageNumber, optionsPerPage, tickerSymbol, selectedDate) {
    //     // Make a request to the /list-options API with page and perPage parameters
    //     $.ajax({
    //         url: '/list-options', // Replace with your API endpoint
    //         method: 'POST',
    //         dataType: 'json',
    //         contentType: 'application/json',
    //         data: JSON.stringify({
    //             tickerSymbol: tickerSymbol,
    //             selectedDate: selectedDate,
    //             expireDate: expireDate,
    //             strike: Number(strike),
    //             page: pageNumber,
    //             perPage: optionsPerPage
    //         }),
    //         success: function(response) {
    //             console.log(response)
    //             // Update the options list with the received data
    //             updateOptionsList(response.options);

    //             // Update pagination controls
    //             updatePagination(Math.floor(response.total_records / optionsPerPage) + 1, pageNumber);
    //         },
    //         error: function(error) {
    //             console.error('Error fetching data from the API: ' + error.statusText);
    //         }
    //     });
    // }

    // // Function to update the options list with the received data
    // function updateOptionsList(options) {
    //     var optionsList = $("#options-list");
    //     optionsList.empty(); // Clear existing options

    //     // Populate the list with the received options
    //     // Check if options is defined and is an array
    //     if (Array.isArray(options)) {
    //         // Populate the list with the received options
    //         options.forEach(function(option) {
    //             // Extract relevant information from the option object
    //             var strike = option.strike;
    //             var expireDate = option.expire_date;
    //             var cAsk = option.c_ask;
    //             var cBid = option.c_bid;
    //             var cLast = option.c_last;

    //             // Create a formatted string for the option
    //             var optionText = "Strike: " + strike + ", Expire Date: " + expireDate + ", Call Ask: " + cAsk + ", Call Bid: " + cBid + ", Call Last: " + cLast;

    //             // Create a list item for the option and append it to the options list
    //             var listItem = $("<li>").text(optionText);
    //             var calculateButton = $("<button>").text("Calculate Price");
    //             calculateButton.on("click", function() {
    //                 // Call a function to send a request to /calculate-price
    //                 calculatePrice(selectedDate, strike, expireDate);
    //             });
    //             listItem.append(calculateButton);
    //             optionsList.append(listItem);
    //         });
    //     } else {
    //         console.error('Invalid options data:', options);
    //     }
    // }

    // // Function to update the pagination controls
    // function updatePagination(totalPages, currentPage) {
    //     var paginationControls = $("#pagination-controls");
    //     paginationControls.empty(); // Clear existing controls

    //     // Calculate the number of buttons to display (e.g., 10 at a time)
    //     var buttonsToShow = 10;
    //     var startPage = Math.max(currentPage - Math.floor(buttonsToShow / 2), 1);
    //     var endPage = Math.min(startPage + buttonsToShow - 1, totalPages);

    //     // Add "First Page" button
    //     if (currentPage > 1) {
    //         var firstPageButton = $("<button>").text("First Page");
    //         firstPageButton.on("click", function() {
    //             updatePagination(totalPages, 1);
    //         });
    //         paginationControls.append(firstPageButton);
    //     }

    //     // Create "Previous" button if not on the first page
    //     if (currentPage > 1) {
    //         var prevButton = $("<button>").text("Previous");
    //         prevButton.on("click", function() {
    //             fetchAndDisplayOptions(currentPage - 1, optionsPerPage, tickerSymbol, selectedDate);
    //         });
    //         paginationControls.append(prevButton);
    //     }

    //     // Create page number buttons
    //     for (var i = startPage; i <= endPage; i++) {
    //         var pageButton = $("<button>").text(i);
    //         pageButton.on("click", function() {
    //             fetchAndDisplayOptions(parseInt($(this).text()), optionsPerPage, tickerSymbol, selectedDate);
    //         });
    //         paginationControls.append(pageButton);
    //     }

    //     // Create "Next" button if not on the last page
    //     if (currentPage < totalPages) {
    //         var nextButton = $("<button>").text("Next");
    //         nextButton.on("click", function() {
    //             fetchAndDisplayOptions(currentPage + 1, optionsPerPage, tickerSymbol, selectedDate);
    //         });
    //         paginationControls.append(nextButton);
    //     }

    //     // Add "Last Page" button
    //     if (currentPage < totalPages) {
    //         var lastPageButton = $("<button>").text("Last Page");
    //         lastPageButton.on("click", function() {
    //             updatePagination(totalPages, totalPages);
    //         });
    //         paginationControls.append(lastPageButton);
    //     }
    // }

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

                // Scroll to the results
                $('html, body').animate({
                    scrollTop: $("#results").offset().top
                }, 500);
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
        // if (strike && expireDate) {
        //     calculatePrice(selectedDate, strike, expireDate)
        // } else {
        //     // Make the API request after form submission
        //     fetchAndDisplayOptions(1, optionsPerPage, tickerSymbol, selectedDate);
        // }
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
    $("input[name='optionChoice']").change(function() {
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
        $(".rvspotSection").hide();

        // Show the selected section
        if (selectedOption === "symbolTicker") {
            $("#symbolTickerSection").show();
            document.getElementById("symbolTicker").required = true;
            document.getElementsByClassName("rvspotSection").required = false;
            document.getElementsByClassName("rvspotSection").value = 0;
        } else {
            $(".rvspotSection").show();
            document.getElementById("symbolTicker").required = false;
            document.getElementsByClassName("rvspotSection").required = true;
            document.getElementById("symbolTicker").value = "";
        }
    });
});
