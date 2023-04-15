function sendRequest() {
  // Get the text from the text box
  var ticker = document.getElementById("textbox").value;

  // Define the HTTP request options
  var options = {
    method: "POST",
    body: ticker,
    headers: {
      "Content-Type": "text/plain",
    },
  };

  // Send the HTTP request with the fetch() method
  fetch("http://localhost:8000/visualize", options)
    .then(function(response) {
      if (response.status == 200) {
        return response.text();
      }
      throw new Error("Network response was not ok.");
    })
    .then(function(html) {
      var newWindow = open();
      newWindow.document.write(html);
      newWindow.document.close();
    })
    .catch(function(error) {
      console.log("There was a problem with the fetch operation:", error);
    });
}
