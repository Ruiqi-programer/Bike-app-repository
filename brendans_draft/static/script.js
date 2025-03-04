document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const logoutBtn = document.getElementById("logout");
    let map;
    let markers = [];

    // Handle Login
    loginForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        fetch("http://127.0.0.1:5000/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.token) {
                localStorage.setItem("token", data.token);
                document.getElementById("login-section").style.display = "none";
                document.getElementById("logout-section").style.display = "block";
                document.getElementById("weather-section").style.display = "block";
                document.getElementById("map").style.display = "block";

                loadGoogleMaps();
                fetchWeather();
            } else {
                document.getElementById("login-error").innerText = "Invalid credentials.";
            }
        })
        .catch(error => console.error("Login error:", error));
    });

    // Handle Logout
    logoutBtn.addEventListener("click", function () {
        localStorage.removeItem("token");
        location.reload();
    });

    // Load Google Maps dynamically
    function loadGoogleMaps() {
        const script = document.createElement("script");
        script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyCnx_FmRZPRQYeqfTrLghRVsb6YwWFBEuU&callback=initMap`;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
    }

    // Initialize Google Maps
    window.initMap = function () {
        console.log("Initializing Google Map...");
        const mapElement = document.getElementById("map");

        if (!mapElement) {
            console.error(" Map element not found!");
            return;
        }

        map = new google.maps.Map(mapElement, {
            center: { lat: 53.349805, lng: -6.26031 },
            zoom: 13
        });

        fetchStations();
        setInterval(fetchStations, 10000);
    };

    // Fetch and display weather data
    function fetchWeather() {
        fetch("/api/weather", {
            headers: { Authorization: "Bearer " + localStorage.getItem("token") }
        })
        .then(response => response.json())
        .then(data => {
            if (!data || !data.current) {
                console.error(" No weather data received.");
                return;
            }

            // Display current weather
            const current = data.current;
            document.getElementById("temp").innerText = current.temp ?? "N/A";
            document.getElementById("feels_like").innerText = current.feels_like ?? "N/A";
            document.getElementById("humidity").innerText = current.humidity ?? "N/A";
            document.getElementById("wind_speed").innerText = current.wind_speed ?? "N/A";
            document.getElementById("clouds").innerText = current.clouds ?? "N/A";

            // Display past 5 hours of weather
            if (Array.isArray(data.hourly)) {
                const hourlyContainer = document.getElementById("hourly-forecast");
                hourlyContainer.innerHTML = "<h3>Past 5 Hours</h3>";

                data.hourly.slice(-5).reverse().forEach(hour => {
                    const hourDate = new Date(hour.dt);
                    if (!isNaN(hourDate.getTime()) && hour.temp !== undefined) {
                        hourlyContainer.innerHTML += `
                            <p><strong>${formatTime(hourDate)}</strong>: ${hour.temp}°C, ${hour.humidity}% Humidity, ${hour.wind_speed} km/h Wind</p>
                        `;
                    } else {
                        console.warn("⚠️ Skipping hour due to invalid timestamp:", hour);
                    }
                });
            }

            // Display next 3 days of weather
            if (Array.isArray(data.daily)) {
                const dailyContainer = document.getElementById("daily-forecast");
                dailyContainer.innerHTML = "<h3>Daily</h3>";

                let today = new Date();
                today.setHours(0, 0, 0, 0);

                const futureDays = data.daily.filter(day => {
                    const dayDate = new Date(day.dt);
                    return !isNaN(dayDate.getTime()) && dayDate >= today;
                }).slice(0, 3);

                if (futureDays.length === 0) {
                    dailyContainer.innerHTML += "<p>No future forecast available.</p>";
                } else {
                    futureDays.forEach(day => {
                        const dayDate = new Date(day.dt);
                        dailyContainer.innerHTML += `
                            <p><strong>${formatDate(dayDate)}</strong>: ${day.temp_day}°C (Min: ${day.temp_min}°C, Max: ${day.temp_max}°C), ${day.humidity}% Humidity</p>
                        `;
                    });
                }
            }
        })
        .catch(error => console.error("Weather fetch error:", error));
    }

    // Fetch and display bike stations
    function fetchStations() {
        fetch("/api/stations", {
            headers: { Authorization: "Bearer " + localStorage.getItem("token") }
        })
        .then(response => response.json())
        .then(data => {
            clearMarkers();

            if (!Array.isArray(data) || data.length === 0) {
                console.warn("⚠️ No station data available.");
                return;
            }

            data.forEach(station => {
                let markerColor = station.available_bikes === 0 ? "red" :
                                  station.available_bikes < 5 ? "orange" : "green";

                let markerIcon = {
                    url: `https://maps.google.com/mapfiles/ms/icons/${markerColor}-dot.png`
                };

                const marker = new google.maps.Marker({
                    position: { lat: station.latitude, lng: station.longitude },
                    map: map,
                    icon: markerIcon,
                    title: station.name
                });

                const infoWindow = new google.maps.InfoWindow({
                    content: `<h3>${station.name}</h3>
                              <p>🚲 Bikes Available: <b>${station.available_bikes ?? "N/A"}</b></p>
                              <p>🅿️ Stands Available: <b>${station.available_bike_stands ?? "N/A"}</b></p>
                              <p>Total Stands: ${station.total_bike_stands}</p>`
                });

                marker.addListener("click", () => infoWindow.open(map, marker));
                markers.push(marker);
            });
        })
        .catch(error => console.error("Error fetching station data:", error));
    }

    // Remove all existing markers from the map
    function clearMarkers() {
        markers.forEach(marker => marker.setMap(null));
        markers = [];
    }

    // Format time from timestamp
    function formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
    }

    // Format date from timestamp
    function formatDate(date) {
        return date.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
    }

    // Ensure script runs when already logged in
    if (localStorage.getItem("token")) {
        document.getElementById("login-section").style.display = "none";
        document.getElementById("logout-section").style.display = "block";
        document.getElementById("weather-section").style.display = "block";
        document.getElementById("map").style.display = "block";

        loadGoogleMaps();
        fetchWeather();
    }
});
