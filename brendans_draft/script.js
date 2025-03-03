// Initialize the map
var map = L.map('map').setView([53.349805, -6.26031], 13);

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Function to update bike stations data
function updateMap() {
    const token = localStorage.getItem("token");
    console.log("Fetching stations with token:", token);

    if (!token) {
        console.error("No authentication token found!");
        return;
    }

    fetch("http://127.0.0.1:5000/api/stations", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Bike Stations Data:", data);  // Debugging

        if (!Array.isArray(data)) {
            console.error("Unexpected API response for stations:", data);
            return;
        }

        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });

        data.forEach(station => {
            let markerColor = station.available_bikes === 0 ? "red" :
                              station.available_bikes < 5 ? "orange" : "green";

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

        setTimeout(() => {
            map.invalidateSize();
        }, 500);
    })
    .catch(error => console.error("Error fetching bike data:", error));
}

// Function to update weather data
function updateWeather() {
    const token = localStorage.getItem("token");

    fetch("http://127.0.0.1:5000/api/weather", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Weather Data:", data);

        if (Object.keys(data).length === 0) {
            document.getElementById("weather-section").innerHTML = "<p>Weather data unavailable.</p>";
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

// Function to log in the user
function loginUser(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("http://127.0.0.1:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem("token", data.token);
            document.getElementById("login-section").style.display = "none";
            document.getElementById("logout-section").style.display = "block";
            document.getElementById("weather-section").style.display = "block";
            document.getElementById("map").style.display = "block";
            updateMap();
            updateWeather();
        } else {
            document.getElementById("login-error").textContent = data.error;
        }
    })
    .catch(error => console.error("Login error:", error));
}

// Function to log out the user
function logoutUser() {
    localStorage.removeItem("token");
    document.getElementById("login-section").style.display = "block";
    document.getElementById("logout-section").style.display = "none";
    document.getElementById("weather-section").style.display = "none";
    document.getElementById("map").style.display = "none";
}

// Run initial setup
document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("token")) {
        document.getElementById("login-section").style.display = "none";
        document.getElementById("logout-section").style.display = "block";
        document.getElementById("weather-section").style.display = "block";
        document.getElementById("map").style.display = "block";
        updateMap();
        updateWeather();
    } else {
        document.getElementById("login-section").style.display = "block";
        document.getElementById("logout-section").style.display = "none";
        document.getElementById("weather-section").style.display = "none";
        document.getElementById("map").style.display = "none";
    }

    document.getElementById("login-form").addEventListener("submit", loginUser);
    document.getElementById("logout").addEventListener("click", logoutUser);
});
