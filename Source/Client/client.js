fetch("http://localhost:8000/visualize")
  .then(function(response) {
    console.log("success!", response);
  })
  .catch(function(err) {
    console.warn("Error", err);
  });
