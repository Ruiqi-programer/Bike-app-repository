// Initialize the map
var map = L.map('map').setView([53.349805, -6.26031], 13); // Dublin coordinates

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

function updateMap() {
    fetch("http://127.0.0.1:5000/api/stations")
        .then(response => response.json())
        .then(data => {
            console.log("Bike Stations Data:", data); 

            // Clear old markers
            map.eachLayer(layer => {
                if (layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });

            // Loop through each station and add a marker
            data.forEach(station => {
                let markerColor = "blue"; // Default color
                if (station.available_bikes === 0) {
                    markerColor = "red";
                } else if (station.available_bikes < 5) {
                    markerColor = "orange";
                } else {
                    markerColor = "green";
                }

                let markerIcon = L.icon({
                    iconUrl: `https://maps.google.com/mapfiles/ms/icons/${markerColor}-dot.png`,
                    iconSize: [32, 32],
                    iconAnchor: [16, 32],
                    popupAnchor: [0, -30]
                });

                L.marker([station.latitude, station.longitude], { icon: markerIcon })
                  .addTo(map)
                  .bindPopup(
                    `<b>${station.name}</b><br>
                     🚲 Available Bikes: <b>${station.available_bikes ?? "N/A"}</b><br>
                     🅿️ Available Stands: <b>${station.available_bike_stands ?? "N/A"}</b><br>
                     Total Stands: ${station.total_bike_stands}`
                  );
            });
        })
        .catch(error => console.error("Error fetching bike data:", error));
}

function updateWeather() {
    fetch("http://127.0.0.1:5000/api/weather")
        .then(response => response.json())
        .then(data => {
            console.log("Weather Data:", data); 

            if (Object.keys(data).length === 0) {
                document.getElementById("weather").innerHTML = "<p>Weather data unavailable.</p>";
                return;
            }

            document.getElementById("temp").textContent = data.temp;
            document.getElementById("feels_like").textContent = data.feels_like;
            document.getElementById("humidity").textContent = data.humidity;
            document.getElementById("wind_speed").textContent = data.wind_speed;
            document.getElementById("clouds").textContent = data.clouds;
        })
        .catch(error => console.error("Error fetching weather data:", error));
}

updateMap(); // Load bike stations initially
updateWeather(); // Load weather initially
setInterval(updateMap, 300000); // Refresh bike data every 5 minutes
setInterval(updateWeather, 3600000); // Refresh weather every hour
