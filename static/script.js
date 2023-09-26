$(document).ready(function() {
    var optionsPerPage = 10;
    var tickerSymbol
    var selectedDate
    // Fetch data from the API (assuming it returns an array)
    $.ajax({
        url: '/ticker-symbols', // Replace with your API endpoint
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            populateDropdown(data);
        },
        error: function(error) {
            console.error('Error fetching data from the API: ' + error.statusText);
        }
    });

    // Function to populate the first dropdown
    function populateDropdown(options) {
        var dropdown = document.getElementById("optionSelect1");

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
    // _todo update min/max
    year = 2019;
    $("#datepicker").datepicker({
        minDate: new Date(year, 0, 1),
        maxDate: new Date(year+1, 12, 30)
    });


    // Function to fetch options from the API and display them
    function fetchAndDisplayOptions(pageNumber, optionsPerPage, tickerSymbol, selectedDate) {
        // Make a request to the /list-options API with page and perPage parameters
        $.ajax({
            url: '/list-options', // Replace with your API endpoint
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify({
                tickerSymbol: tickerSymbol,
                selectedDate: selectedDate,
                page: pageNumber,
                perPage: optionsPerPage
            }),
            success: function(response) {
                console.log(response)
                // Update the options list with the received data
                updateOptionsList(response);

                // Update pagination controls
                updatePagination(optionsPerPage, pageNumber);
            },
            error: function(error) {
                console.error('Error fetching data from the API: ' + error.statusText);
            }
        });
    }

    // Function to update the options list with the received data
    function updateOptionsList(options) {
        var optionsList = $("#options-list");
        optionsList.empty(); // Clear existing options

        // Populate the list with the received options
        // Check if options is defined and is an array
        if (Array.isArray(options)) {
            // Populate the list with the received options
            options.forEach(function(option) {
                // Extract relevant information from the option object
                var strike = option.strike;
                var expireDate = option.expire_date;
                var cAsk = option.c_ask;
                var cBid = option.c_bid;
                var cLast = option.c_last;

                // Create a formatted string for the option
                var optionText = "Strike: " + strike + ", Expire Date: " + expireDate + ", Call Ask: " + cAsk + ", Call Bid: " + cBid + ", Call Last: " + cLast;

                // Create a list item for the option and append it to the options list
                var listItem = $("<li>").text(optionText);
                var calculateButton = $("<button>").text("Calculate Price");
                calculateButton.on("click", function() {
                    // Call a function to send a request to /calculate-price
                    calculatePrice(selectedDate, strike, expireDate, option.c_last);
                });
                listItem.append(calculateButton);
                optionsList.append(listItem);
            });
        } else {
            console.error('Invalid options data:', options);
        }
    }

    // Function to update the pagination controls
    function updatePagination(totalPages, currentPage) {
        var paginationControls = $("#pagination-controls");
        paginationControls.empty(); // Clear existing controls

        // Create "Previous" button if not on the first page
        if (currentPage > 1) {
            var prevButton = $("<button>").text("Previous");
            prevButton.on("click", function() {
                fetchAndDisplayOptions(currentPage - 1, optionsPerPage);
            });
            paginationControls.append(prevButton);
        }

        // Create page number buttons
        for (var i = 1; i <= totalPages; i++) {
            var pageButton = $("<button>").text(i);
            pageButton.on("click", function() {
                fetchAndDisplayOptions(parseInt($(this).text()), optionsPerPage, tickerSymbol, selectedDate);
            });
            paginationControls.append(pageButton);
        }

        // Create "Next" button if not on the last page
        if (currentPage < totalPages) {
            var nextButton = $("<button>").text("Next");
            nextButton.on("click", function() {
                fetchAndDisplayOptions(currentPage + 1, optionsPerPage, tickerSymbol, selectedDate);
            });
            paginationControls.append(nextButton);
        }
    }

    function calculatePrice(selectedDate, strike, expireDate, price) {
        var requestData = {
            selectedDate: selectedDate,
            strike: strike,
            expireDate: expireDate,
            price: price
        };
    
        $.ajax({
            url: '/calculate-price', // Replace with your API endpoint
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            success: function(response) {
                // Handle the response from the calculation API
                console.log('Calculation result:', response);
                // Create an image element and set its src attribute
                var imageElement = $('<img>').attr('src', 'static/foo.png?t=' + new Date().getTime());
                
                // Append the image to the image container
                $('#image-container').empty();
                $('#image-container').append(imageElement);
                // You can display the result or take further actions here
            },
            error: function(error) {
                console.error('Error calculating price:', error.statusText);
            }
        });
    }

    // Handle form submission
    $("#optionForm").submit(function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Get selected ticker symbol and date from the form
        tickerSymbol = $("#optionSelect1").val();
        selectedDate = $("#datepicker").val();

        // Make the API request after form submission
        fetchAndDisplayOptions(1, optionsPerPage, tickerSymbol, selectedDate);
    });
});
