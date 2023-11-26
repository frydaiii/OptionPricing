import { Sleep, CreateNestedList } from "./utils.js"

async function UpdateCalculatePriceResult(calResponse) {
  var still_update = true;
  var limit = 200;
  var count = 0;
  while (still_update && ++count < limit) {
    await Sleep(1500);

    if (!("gp_id" in calResponse)) {
      calResponse["gp_id"] = "";
    }

    if (!("garch_id" in calResponse)) {
      calResponse["garch_id"] = "";
    }

    console.log(calResponse)

    $.ajax({
      url: '/calculate-price-status',
      method: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify(calResponse),
      success: function (response) {
        if (response["done"]) {
          still_update = false;
        }
        $('#result-prices').empty();
        $('#result-prices').append(CreateNestedList(response));
      },
      error: function (error) {
        console.error('Error calculating price:', error.statusText);
      }
    });
  }
}

async function UpdateCalculatePrice2Result(calResponse) {
  var still_update = true;
  var limit = 200;
  var count = 0;
  while (still_update && ++count < limit) {
    await Sleep(2000);

    $.ajax({
      url: '/calculate-price-2-status',
      method: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify(calResponse),
      success: function (response) {
        // Handle the response from the calculation API
        console.log('Calculation result:', response);
        if (response["done"]) {

          // Create an image element and set its src attribute
          var imageElement = $('<img>').attr('src', response["img1"] + '?t=' + new Date().getTime());
          var imageElement2 = $('<img>').attr('src', response["img2"] + '?t=' + new Date().getTime());

          // Append the image to the image container
          $('#image-container-2').empty();
          $('#image-container-2').append(imageElement);
          $('#image-container-2').append(imageElement2);
          still_update = false;
        } else {
          $('#image-container-2').empty();
          $('#image-container-2').append(CreateNestedList(response));
        }
      },
      error: function (error) {
        console.error('Error calculating price:', error.statusText);
      }
    });
  }
}

export { UpdateCalculatePrice2Result, UpdateCalculatePriceResult }
