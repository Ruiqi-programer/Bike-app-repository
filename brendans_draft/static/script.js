let map;
let markers = [];
let hourlyDataCache = [];

const activeFilters = {
    search: "",
    hasBikes: false,
    hasStands: false,
    notEmpty: false,
    notFull: false
};

window.initMap = function () {
    console.log("🗺️ Google Maps API loaded");
    loadMapAndStations();
};

function loadMapAndStations() {
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        console.error("Map element not found!");
        return;
    }

    map = new google.maps.Map(mapElement, {
        center: { lat: 53.349805, lng: -6.26031 },
        zoom: 13,
        disableDefaultUI: true
    });

    fetchStations();
    setInterval(fetchStations, 60000);
}

document.addEventListener("DOMContentLoaded", () => {
    fetchWeather();
    setupWeatherModal();
    setupFilters();
});

function setupFilters() {
    const search = document.getElementById("station-search");
    const bikes = document.getElementById("filter-bikes");
    const stands = document.getElementById("filter-stands");
    const notEmpty = document.getElementById("filter-not-empty");
    const notFull = document.getElementById("filter-not-full");

    if (!search || !bikes || !stands || !notEmpty || !notFull) return;

    search.addEventListener("input", e => {
        activeFilters.search = e.target.value.toLowerCase();
        fetchStations();
    });

    bikes.addEventListener("change", e => {
        activeFilters.hasBikes = e.target.checked;
        fetchStations();
    });

    stands.addEventListener("change", e => {
        activeFilters.hasStands = e.target.checked;
        fetchStations();
    });

    notEmpty.addEventListener("change", e => {
        activeFilters.notEmpty = e.target.checked;
        fetchStations();
    });

    notFull.addEventListener("change", e => {
        activeFilters.notFull = e.target.checked;
        fetchStations();
    });
}

function smoothZoom(map, targetZoom, step = 1) {
    const currentZoom = map.getZoom();
    if (currentZoom === targetZoom) return;

    const zoomDirection = currentZoom < targetZoom ? 1 : -1;
    let zoom = currentZoom;

    const zoomInterval = setInterval(() => {
        zoom += zoomDirection;
        map.setZoom(zoom);

        if (zoom === targetZoom) {
            clearInterval(zoomInterval);
        }
    }, 100);
}

function fetchStations() {
    fetch("/api/stations")
        .then(response => response.json())
        .then(data => {
            clearMarkers();
            if (!Array.isArray(data)) return;

            data.forEach(station => {
                const nameMatch = station.name.toLowerCase().includes(activeFilters.search);
                const hasBikes = station.available_bikes > 0;
                const hasStands = station.available_bike_stands > 0;
                const isNotEmpty = station.available_bikes > 0;
                const isNotFull = station.available_bike_stands > 0;

                if (
                    (activeFilters.search && !nameMatch) ||
                    (activeFilters.hasBikes && !hasBikes) ||
                    (activeFilters.hasStands && !hasStands) ||
                    (activeFilters.notEmpty && !isNotEmpty) ||
                    (activeFilters.notFull && !isNotFull)
                ) {
                    return;
                }

                const color = station.available_bikes === 0 ? "#e74c3c" :
                              station.available_bikes < 5 ? "#f39c12" : "#2ecc71";

                const markerIcon = createMarkerIcon(color, station.available_bikes);

                const marker = new google.maps.Marker({
                    position: {
                        lat: parseFloat(station.latitude),
                        lng: parseFloat(station.longitude)
                    },
                    map: map,
                    icon: markerIcon,
                    title: station.name
                });

                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <h3>${station.name}</h3>
                        <p>🚲 Bikes Available: <b>${station.available_bikes}</b></p>
                        <p>🅿️ Stands Available: <b>${station.available_bike_stands}</b></p>
                        <p>Total Stands: ${station.total_bike_stands}</p>
                    `
                });

                marker.addListener("click", () => {
                    map.panTo(marker.getPosition());
                    smoothZoom(map, 17);
                    infoWindow.open(map, marker);
                });

                markers.push(marker);
            });
        })
        .catch(error => console.error("❌ Error in fetchStations:", error));
}

function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}

function createMarkerIcon(color, count) {
    const svg = `
      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="42" viewBox="0 0 40 50">
        <path d="M20 0C9 0 0 9 0 20c0 11 20 30 20 30s20-19 20-30c0-11-9-20-20-20z"
          fill="${color}" stroke="black" stroke-width="2"/>
        <text x="20" y="28"
          font-size="15"
          font-family="Arial"
          font-weight="bold"
          text-anchor="middle"
          fill="black">
          ${count}
        </text>
      </svg>
    `;
    return {
      url: "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(svg),
      scaledSize: new google.maps.Size(32, 42),
      anchor: new google.maps.Point(16, 42)
    };
}

function fetchWeather() {
    fetch("/api/weather")
        .then(response => response.json())
        .then(data => {
            const current = data.current;
            if (!current) return;

            showCurrentWeather(current);
            hourlyDataCache = data.hourly || [];
            showDailyForecast(data.daily || []);
            showHourlyTimeline(data.hourly || []);
        })
        .catch(error => console.error("Weather fetch error:", error));
}

function setupWeatherModal() {
    const weatherBtn = document.getElementById("weather-btn");
    const weatherModal = document.getElementById("weather-modal");
    const closeModal = document.querySelector(".close");

    if (!weatherBtn || !weatherModal || !closeModal) return;

    weatherBtn.addEventListener("click", () => {
        weatherModal.style.display = "block";
        setTimeout(drawHourlyChart, 100);
    });

    closeModal.addEventListener("click", () => {
        weatherModal.style.display = "none";
    });

    window.addEventListener("click", event => {
        if (event.target === weatherModal) {
            weatherModal.style.display = "none";
        }
    });
}

function showCurrentWeather(current) {
    const container = document.getElementById("current-weather-info");
    if (!container) return;

    container.innerHTML = `
        <p><strong>🌡️ Temperature:</strong> ${current.temp}°C</p>
        <p><strong>🤗 Feels Like:</strong> ${current.feels_like}°C</p>
        <p><strong>💧 Humidity:</strong> ${current.humidity}%</p>
        <p><strong>🌬️ Wind:</strong> ${current.wind_speed} km/h</p>
        <p><strong>☁️ Clouds:</strong> ${current.clouds}%</p>
    `;
}

function showDailyForecast(daily) {
    const grid = document.getElementById("daily-forecast-grid");
    if (!grid || !Array.isArray(daily)) return;

    grid.innerHTML = "";

    daily.forEach(day => {
        const date = new Date(day.dt);
        const dateString = date.toLocaleDateString(undefined, {
            weekday: "short",
            month: "short",
            day: "numeric"
        });

        const iconCode = day.weather_icon ?? "";
        const iconUrl = iconCode ? `https://openweathermap.org/img/wn/${iconCode}@2x.png` : "";
        const weatherDesc = day.weather_desc ?? "N/A";

        const card = document.createElement("div");
        card.className = "forecast-card";

        card.innerHTML = `
            <h4>${dateString}</h4>
            <div class="forecast-info">
                <img src="${iconUrl}" alt="${weatherDesc}" width="40" onerror="this.src='https://via.placeholder.com/40?text=?'">
                <span>${day.temp_day}° / ${day.temp_min}°C</span>
            </div>
            <div class="forecast-info">
                <small>${weatherDesc}</small>
            </div>
        `;

        grid.appendChild(card);
    });
}

function drawHourlyChart() {
    const hourly = hourlyDataCache;
    if (!hourly || hourly.length === 0) return;

    const ctx = document.getElementById("hourly-temp-chart").getContext("2d");

    const labels = [];
    const temps = [];

    hourly.forEach(hour => {
        const date = new Date(hour.dt);
        labels.push(date.toLocaleTimeString([], { hour: "2-digit", hour12: true }));
        temps.push(hour.temp);
    });

    if (window.hourlyChart) {
        window.hourlyChart.destroy();
    }

    window.hourlyChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Temperature (°C)",
                data: temps,
                fill: true,
                borderColor: "rgba(255, 99, 132, 1)",
                backgroundColor: "rgba(255, 99, 132, 0.1)",
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: "12-Hour Temperature Trend",
                    font: { size: 18 }
                }
            },
            scales: {
                x: { ticks: { maxRotation: 30, minRotation: 30 } },
                y: {
                    beginAtZero: false,
                    title: { display: true, text: "Temperature (°C)" }
                }
            }
        }
    });
}

function showHourlyTimeline(hourly) {
    const container = document.getElementById("hourly-timeline");
    if (!container || !Array.isArray(hourly)) return;

    container.innerHTML = "";

    hourly.forEach(hour => {
        const date = new Date(hour.dt);
        const time = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: true });
        const icon = hour.weather_desc || "";
        const wind = `${hour.wind_speed} m/s`;

        const box = document.createElement("div");
        box.className = "hourly-timeline-box";
        box.innerHTML = `
            <strong>${time}</strong>
            <p>${icon}</p>
            <p>💨 ${wind}</p>
        `;
        container.appendChild(box);
    });
}