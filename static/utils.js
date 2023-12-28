function Sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function CreateNestedList(data) {
  const list = document.createElement('ul');

  for (let key in data) {
    const listItem = document.createElement('li');
    listItem.textContent = key;

    if (typeof data[key] === 'object' && data[key] !== null) {
      const nestedList = CreateNestedList(data[key]);
      listItem.appendChild(nestedList);
    } else {
      const itemValue = document.createElement('span');
      itemValue.textContent = " " + JSON.stringify(data[key]);
      listItem.appendChild(itemValue);
    }

    list.appendChild(listItem);
  }

  return list;
}

function GetCurrentDate() {
  const today = new Date();

  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
  const day = String(today.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
}

function GetExpirations(ticker, type, trading_date) {
  var req = {
    "ticker": ticker,
    "type": type,
    "trading_date": trading_date
  }
  var expire_dates;
  $.ajax({
    url: '/expirations',
    method: 'POST',
    async: false,
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(req),
    success: function (response) {
      expire_dates = response;
    },
    error: function (error) {
      console.error('Error calculating price:', error.statusText);
    }
  });

  return expire_dates;
}

function PopulateDropdown(options, option_select_id) {
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
export { Sleep, CreateNestedList, GetCurrentDate, GetExpirations, PopulateDropdown }