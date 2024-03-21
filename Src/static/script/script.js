
function changeClass0(){
  var element = document.querySelector("#nr0");
  element.classList.replace("options", "selected");
  var button = document.querySelector("#button0");
  button.classList.replace("options", "selected");

  var element2 = document.querySelector("#nr1");
  element2.classList.replace("selected", "options");
  var button1 = document.querySelector("#button1");
  button1.classList.replace("selected", "options");

  var element3 = document.querySelector("#nr2");
  element3.classList.replace("selected", "options");
  var button2 = document.querySelector("#button2");
  button2.classList.replace("selected", "options");
}

function changeClass1(){
  var element = document.querySelector("#nr1");
  element.classList.replace("options", "selected");
  var button1 = document.querySelector("#button1");
  button1.classList.replace("options", "selected");

  var element2 = document.querySelector("#nr0");
  element2.classList.replace("selected", "options");
  var button = document.querySelector("#button0");
  button.classList.replace("selected", "options");

  var element3 = document.querySelector("#nr2");
  element3.classList.replace("selected", "options");
  var button2 = document.querySelector("#button2");
  button2.classList.replace("selected", "options");
}

function changeClass2(){
  var element = document.querySelector("#nr2");
  element.classList.replace("options", "selected");
  var button2 = document.querySelector("#button2");
  button2.classList.replace("options", "selected");

  var element2 = document.querySelector("#nr0");
  element2.classList.replace("selected", "options");
  var button = document.querySelector("#button0");
  button.classList.replace("selected", "options");

  var element3 = document.querySelector("#nr1");
  element3.classList.replace("selected", "options");
  var button1 = document.querySelector("#button1");
  button1.classList.replace("selected", "options");
  
}

//start coordinates for the map (its coordinates for stockholm)
var start = { lat: 59.326038, lng:17.8172531};

let directionsService, directionsRenderer

//initialize the Google Map
function initMap(){
  
var mapOptions = {
  center: start,
  zoom: 4,
};

map = new google.maps.Map(document.getElementById('googleMap'), mapOptions);

directionsService = new google.maps.DirectionsService();
directionsRenderer = new google.maps.DirectionsRenderer();
directionsRenderer.setMap(map);

}

// Make a route and then display it on the map
// grids willl contain the route between warehouses for delivery
// buyNsell will contain the buyers and seller for the routes and their closest warehouses
// Start of new function for displaying routes that takes waypoints (not finished)
// function drawMap(grids, buyNsell) {

//   var mapOptions = {
//     center: start,
//     zoom: 4,
//   };

//   function renderDirections(result) {
//     var directionsRenderer = new google.maps.DirectionsRenderer();
//     directionsRenderer.setMap(map);
//     directionsRenderer.setDirections(result);
//   }

//   function requestDirections2(start, end) {
//     let req = {
//       origin: start,
//       destination: end,
//       waypoints: theRoute,
//       travelMode: "DRIVING",
//     };
//     directionsService.route(req, function (result, status) {
//       if (status == "OK") {
//         renderDirections(result);
//       }
//     })
//   }

//   function requestDirections(start, end, theRoute) {
//     let req = {
//       origin: start,
//       destination: end,
//       waypoints: theRoute,
//       travelMode: "DRIVING",
//     };
//     directionsService.route(req, function (result, status) {
//       if (status == "OK") {
//         renderDirections(result);
//       }
//     })
//   }

//   var x = 0
//   while (x < grids.length){
//     let tempG = grids.slice(1, grids.length-1);
//     tempG = tempG.split();
//     requestDirections(grids[0], grids[grids.length-1], tempG);
//     requestDirections2(buyNsell[0], buyNsell[2]);
//     requestDirections2(buyNsell[1], buyNsell[3]);
//     x = x + 1
//   }

// }

//////////////////////////////////////////////////////////////////////////////////////////////

//Old function for displaying routes, just takes the easiest way by car with google maps
function calcRoute(source, destination){

  var mapOptions = {
    center: start,
    zoom: 3,
  };

  map = new google.maps.Map(document.getElementById('googleMap'), mapOptions);

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer();
  directionsRenderer.setMap(map);

  var rendererOptions = {
    preserveViewport: true,
    suppressMarkers: false,
  };

  var sourceSplit = source.split(', ');
  var destinationSplit = destination.split(', ');

  if (destinationSplit[1] != null) {

    if(destinationSplit[2] == null){
      var routes = [{ origin: sourceSplit[0], destination: destinationSplit[0] }, { origin: sourceSplit[0], destination: destinationSplit[1] }];
    }else{
      var routes = [{ origin: sourceSplit[0], destination: destinationSplit[0] }, { origin: sourceSplit[0], destination: destinationSplit[1]}, { origin: sourceSplit[0], destination: destinationSplit[2] }];
    }
    const drawContinental = (route) => {
      var request = {
        origin: route.origin,
        destination: route.destination,
        travelMode: "DRIVING"
      };

      var directionsRenderer = new google.maps.DirectionsRenderer(rendererOptions);
      directionsRenderer.setMap(map);

      directionsService.route(request, function (result, status) {

        if (status == "OK") {
          directionsRenderer.setDirections(result);
        }
      });
    };

    routes.forEach(drawContinental);

  }
  else {
    let req = {
      origin: source,
      destination: destination,
      travelMode: "DRIVING",
    };
    directionsService.route(req, function (result, status) {
      if (status == "OK") {
        directionsRenderer.setDirections(result)
      }
    })
  }

}

function changeInfo(x){
  const info = getInfo();
  // const gridInfo = getGrid(x);
  const buy = getBuyer();
  const sellerInfo = getSellerInfo();

  //Calls function to display a route in the google map
  calcRoute(sellerInfo[1], sellerInfo[3]+','+sellerInfo[7]+','+sellerInfo[11]);

  // console.log(gridInfo);
  //Sets the text with right info on results in the div with id info
  document.getElementById("info").innerHTML = "<div><h1>Buyer</h1><p>Location: "+sellerInfo[1]+","+info[0]+"</p><p>Score = "+buy[3]+ "</p><p>Fairness index = "+buy[2]+ "<p>Eco score = "+buy[4]+"</p></div><div class='infoInner'><div class='infoInnerDiv'><h2>Seller 0</h2></p><p>Location = "+sellerInfo[3]+","+info[1]+ "</p></div><div class='infoInnerDiv'><h2>Seller 1</h2></p><p>Location = "+sellerInfo[7]+","+info[3]+"</div></div><div class='infoInnerDiv'><h2>Seller 2</h2></p><p>Location = "+sellerInfo[11]+","+info[5];

}
