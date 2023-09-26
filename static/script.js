$(document).ready(function() {
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
    $("#datepicker").datepicker();

    // Handle form submission
    $("#optionForm").submit(function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Get selected ticker symbol and date from the form
        var tickerSymbol = $("#optionSelect1").val();
        var selectedDate = $("#datepicker").val();

        // Make a request to the /list-options API
        $.ajax({
            url: '/list-options', // Replace with your API endpoint
            method: 'POST',
            dataType: 'json',
            data: {
                tickerSymbol: tickerSymbol,
                selectedDate: selectedDate
            },
            success: function(response) {
                // Handle the response from the API here
                console.log(response);
            },
            error: function(error) {
                console.error('Error sending request to the API: ' + error.statusText);
            }
        });
    });
});
