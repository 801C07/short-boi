document.addEventListener("DOMContentLoaded", function () {
  // markWarning
  // markSuccess

  // Add event listener to the button
  // document.querySelector('#markDanger').addEventListener('click', markTicker('bg-danger'));

  // document.querySelector('#markWarning').addEventListener('click', markTicker('bg-warning'));
  // document.querySelector('#markSuccess').addEventListener('click', markTicker('bg-success'));

  //only call the function when the buttons are clicked:
  document.querySelector("#markDanger").addEventListener("click", function () {
    markTicker("bg-danger");
  });

  document.querySelector("#markWarning").addEventListener("click", function () {
    markTicker("bg-warning");
  });

  document.querySelector("#markSuccess").addEventListener("click", function () {
    markTicker("bg-success");
  });
});

function markTicker(status) {
  console.log("marking status", status);
  // get ticker from url
  const url = window.location.href;
  const urlParts = url.split("/");
  const ticker = urlParts[urlParts.length - 1];

  $.ajax({
    url: `/${ticker}`,
    type: "PUT",
    dataType: "json",
    data: JSON.stringify({
      status: status,
    }),
    success: function (response) {
      console.log(response);
    },
  });
}
