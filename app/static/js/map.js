// map.js
let map;
let markers = [];
let currentInfoWindow = null;
let predictionChart = null;
let fetches = [];

const activeFilters = {
  search: "",
  hasBikes: false,
  hasStands: false,
  notEmpty: false,
  notFull: false,
};

export async function loadMapAndStations() {
  const loadingEl = document.getElementById("loading");
  if (loadingEl) loadingEl.style.display = "flex";

  const mapElement = document.getElementById("map");
  if (!mapElement) {
    console.error("Map element not found!");
    return;
  }

  map = new google.maps.Map(mapElement, {
    center: { lat: 53.349805, lng: -6.26031 },
    zoom: 14,
    disableDefaultUI: true,
    mapId: "8adf177586ed1224",
    gestureHandling: "greedy",
  });

  fetchStations();
  setInterval(fetchStations, 60000);
}

export function setupFilters() {
  const search = document.getElementById("station-search");
  const bikes = document.getElementById("filter-bikes");
  const stands = document.getElementById("filter-stands");
  const notEmpty = document.getElementById("filter-not-empty");
  const notFull = document.getElementById("filter-not-full");

  if (!search || !bikes || !stands || !notEmpty || !notFull) return;

  search.addEventListener("input", (e) => {
    activeFilters.search = e.target.value.toLowerCase();
    fetchStations();
  });

  bikes.addEventListener("change", (e) => {
    activeFilters.hasBikes = e.target.checked;
    fetchStations();
  });

  stands.addEventListener("change", (e) => {
    activeFilters.hasStands = e.target.checked;
    fetchStations();
  });

  notEmpty.addEventListener("change", (e) => {
    activeFilters.notEmpty = e.target.checked;
    fetchStations();
  });

  notFull.addEventListener("change", (e) => {
    activeFilters.notFull = e.target.checked;
    fetchStations();
  });
}

function fetchStations() {
  const loadingEl = document.getElementById("loading");
  const startTime = Date.now();
  fetch("/api/stations")
    .then((response) => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then((data) => {
      clearMarkers();
      if (!Array.isArray(data) || data.length === 0) {
        console.warn("No station data received");
        return;
      }

      data.forEach((station) => {
        const nameMatch = station.name
          .toLowerCase()
          .includes(activeFilters.search);
        const hasBikes = station.available_bikes > 0;
        const hasStands = station.available_bike_stands > 0;
        const isNotEmpty = hasBikes;
        const isNotFull = hasStands;

        if (
          (activeFilters.search && !nameMatch) ||
          (activeFilters.hasBikes && !hasBikes) ||
          (activeFilters.hasStands && !hasStands) ||
          (activeFilters.notEmpty && !isNotEmpty) ||
          (activeFilters.notFull && !isNotFull)
        ) {
          return;
        }

        const color =
          station.available_bikes === 0
            ? "#e74c3c"
            : station.available_bikes < 5
            ? "#f39c12"
            : "#2ecc71";

        const marker = new google.maps.marker.AdvancedMarkerElement({
          position: {
            lat: parseFloat(station.latitude),
            lng: parseFloat(station.longitude),
          },
          map,
          content: createMarkerIcon(color, station.available_bikes),
          title: station.name,
        });

        const infoWindow = new google.maps.InfoWindow({
          content: `
              <div class="info-window">
                <h3>${station.name}</h3>
                <p>🚲 Bikes Available: <b>${station.available_bikes}</b></p>
                <p>🅿️ Stands Available: <b>${station.available_bike_stands}</b></p>
                <p>Total Stands: <b>${station.total_bike_stands}</b></p>
                <div id="chart_div_${station.station_id}" class="station-chart"></div>
                <button id="view-prediction-btn"
                data-station-id="${station.station_id}"
                data-station-name="${station.name}">
                INFO BOARD
                </button>
              </div>
          `,
        });

        marker.addListener("gmp-click", () => {
          // close previous InfoWindow
          if (currentInfoWindow) {
            currentInfoWindow.close();
          }
          // open current InfoWindow
          // smoothZoom(map, 16);
          map.panTo(marker.position);

          infoWindow.open(map, marker);

          currentInfoWindow = infoWindow;

          infoWindow.addListener("domready", () => {
            const chartElement = document.getElementById(
              `chart_div_${station.station_id}`
            );
            if (!chartElement) return;

            const chartData = new google.visualization.DataTable();
            chartData.addColumn("string", "Type");
            chartData.addColumn("number", "Count");
            chartData.addRows([
              ["Available Bikes", station.available_bikes],
              ["Free Stands", station.available_bike_stands],
            ]);

            const chart = new google.visualization.BarChart(chartElement);
            chart.draw(chartData, {
              title: "Station Overview",
              legend: { position: "bottom" },
              width: 300,
              height: 200,
              chartArea: { width: "70%", height: "70%" },
            });
          });

          setTimeout(() => {
            const predictionBtn = document.getElementById(
              "view-prediction-btn"
            );

            predictionBtn.addEventListener("click", () => {
              const sid = predictionBtn.dataset.stationId;
              const name = predictionBtn.dataset.stationName;
              window.showPredictionChart(sid, name);
              window.drawHistoricalBikeChartFromJson(sid);
              drawHistoricalWeatherChart();
            });
          });
        });

        markers.push(marker);
      });
    })
    .catch((err) => console.error("❌ Failed to load stations", err))
    .finally(() => {
      const elapsed = Date.now() - startTime;
      const delay = Math.max(0, 500 - elapsed); //  at least 500ms

      setTimeout(() => {
        if (loadingEl) loadingEl.style.display = "none";
      }, delay);
    });
}

function clearMarkers() {
  markers.forEach((marker) => marker.setMap(null));
  markers = [];
}

function createMarkerIcon(color, count) {
  const el = document.createElement("div");
  el.className = "custom-marker";
  el.style.background = color;
  el.style.border = "2px solid black";
  el.style.borderRadius = "50%";
  el.style.width = "32px";
  el.style.height = "32px";
  el.style.display = "flex";
  el.style.alignItems = "center";
  el.style.justifyContent = "center";
  el.style.fontWeight = "bold";
  el.style.color = "black";
  el.innerText = count;
  return el;
}

function smoothZoom(map, targetZoom) {
  const currentZoom = map.getZoom();
  if (currentZoom === targetZoom) return;
  const zoomDirection = currentZoom < targetZoom ? 1 : -1;
  let zoom = currentZoom;
  const zoomInterval = setInterval(() => {
    zoom += zoomDirection;
    map.setZoom(zoom);
    if (zoom === targetZoom) clearInterval(zoomInterval);
  }, 100);
}

export function predict() {
  const stationId = document.getElementById("station_id").value;
  const date = document.getElementById("predict-date").value;
  const time = document.getElementById("predict-time").value;

  if (!stationId || !date || !time) {
    alert("Please fill in all fields.");
    return;
  }

  fetch(`/predict?station_id=${stationId}&date=${date}&time=${time}`)
    .then((res) => res.json())
    .then((data) => {
      const resultDiv = document.getElementById("result");
      if (data.predicted_available_bikes !== undefined) {
        resultDiv.innerHTML = `<p>🚲 Predicted Avaliable Bikes: <strong>${data.predicted_available_bikes}</strong></p>`;
      } else {
        resultDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
      }
    })
    .catch((err) => {
      console.error("Prediction error:", err);
      document.getElementById(
        "result"
      ).innerHTML = `<p style="color:red;">Error fetching prediction.</p>`;
    });
}

export function loadStationsForSelect() {
  fetch("/api/stations")
    .then((res) => res.json())
    .then((stations) => {
      const select = document.getElementById("station_id");
      if (!select) return;

      select.innerHTML = `<option value="">-- Select a station --</option>`;

      stations.forEach((station) => {
        const option = document.createElement("option");
        option.value = station.station_id;
        option.textContent = `${station.name} (ID: ${station.station_id})`;
        select.appendChild(option);
      });
    })
    .catch((err) => {
      console.error("Failed to load stations for select:", err);
    });
}

window.showPredictionChart = function (stationId, stationName) {
  // Open the sidebar
  const sidebar = document.getElementById("station-sidebar");
  sidebar.classList.add("open");

  // Update the station name in the sidebar
  document.getElementById(
    "prediction-station-name"
  ).innerHTML = `Station: <b> ${stationName} </b> <br>Station ID:<b> ${stationId}</b>`;
  const ctx = document.getElementById("prediction-chart")?.getContext("2d");
  if (!ctx) {
    console.error("Chart canvas not found");
    return;
  }
  // Fetch predictions for the next 24 hours
  const now = new Date();
  const predictions = [];
  const labels = [];

  // Generate predictions for each hour in the next 24 hours
  for (let i = 0; i < 24; i++) {
    const futureTime = new Date(now.getTime() + i * 60 * 60 * 1000);
    const date = futureTime.toISOString().split("T")[0];
    const timeString = futureTime.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false, // set to true if you want AM/PM
    });
    labels.push(`${futureTime.getHours()}:00`);

    const fetchPromise = fetch(
      `/predict_range?station_id=${stationId}&date=${date}&time=${timeString}`
    )
      .then((res) => res.json())
      .then((data) => {
        if (data.predicted_available_bikes !== undefined) {
          return data.predicted_available_bikes;
        } else {
          console.error("Prediction error:", data.error);
          return 0;
        }
      })
      .catch((err) => {
        console.error("Prediction fetch error:", err);
        return 0;
      });

    fetches.push(fetchPromise);
  }

  Promise.all(fetches).then((predictions) => {
    updatePredictionChart(labels, predictions);
  });
};

function updatePredictionChart(labels, predictions) {
  const ctx = document.getElementById("prediction-chart").getContext("2d");

  // Destroy existing chart if it exists
  if (predictionChart) {
    predictionChart.destroy();
  }

  predictionChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Predicted Bikes",
          data: predictions,
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          fill: true,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: { display: true, text: "Time (Hour)" },
        },
        y: {
          title: { display: true, text: "Predicted Bikes" },
          beginAtZero: true,
        },
      },
    },
  });
}

window.closePredictionSidebar = function () {
  const sidebar = document.getElementById("station-sidebar");
  sidebar.classList.remove("open");
  if (predictionChart) {
    predictionChart.destroy();
    predictionChart = null;
  }
};

export function setupPredictionModal() {
  const predictModalBtn = document.getElementById("prediction-btn-modal");
  const predictionModal = document.getElementById("prediction-modal");
  const closeModal = predictionModal.querySelector(".close");

  if (!predictModalBtn || !predictionModal || !closeModal) return;

  predictModalBtn.addEventListener("click", () => {
    predictionModal.style.display = "flex";
  });

  closeModal.addEventListener("click", () => {
    predictionModal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === predictionModal) predictionModal.style.display = "none";
  });
}

/* historical bike data */
window.drawHistoricalBikeChartFromJson = async function (stationId) {
  const ctx = document
    .getElementById("historical-bike-chart")
    ?.getContext("2d");
  if (!ctx) return;

  const filePrefix = "/static/data/bike_data/bike_data_2025-02-23_";
  const fileNames = [];

  for (let h = 0; h <= 23; h++) {
    for (let m = 0; m < 60; m += 5) {
      const hh = h.toString().padStart(2, "0");
      const mm = m.toString().padStart(2, "0");
      const fileName = `${filePrefix}${hh}-${mm}-00.json`;
      fileNames.push(fileName);
    }
  }

  const allData = [];

  for (const file of fileNames) {
    try {
      const res = await fetch(file);
      const snapshot = await res.json();
      const found = snapshot.find((s) => s.number == stationId);
      if (found) {
        allData.push({
          time: new Date(found.last_update),
          bikes: found.available_bikes,
          stands: found.available_bike_stands,
        });
      }
    } catch (err) {
      console.warn("❌ Skipped:", file);
    }
  }

  allData.sort((a, b) => a.time - b.time);

  const labels = allData.map((d) =>
    d.time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  );
  const bikes = allData.map((d) => d.bikes);
  const stands = allData.map((d) => d.stands);

  if (window.historicalBikeChart) {
    window.historicalBikeChart.destroy();
  }

  window.historicalBikeChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Available Bikes",
          data: bikes,
          borderColor: "#2ecc71",
          backgroundColor: "rgba(46, 204, 113, 0.2)",
          tension: 0.3,
        },
        {
          label: "Available Stands",
          data: stands,
          borderColor: "#3498db",
          backgroundColor: "rgba(52, 152, 219, 0.2)",
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Historical Bike Availability (1 Day)",
          font: { size: 16 },
        },
      },
      scales: {
        x: {
          ticks: {
            maxTicksLimit: 24,
          },
          title: { display: true, text: "Time" },
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: "Count" },
        },
      },
    },
  });
};

/* historical weather*/
window.drawHistoricalWeatherChart = async function () {
  const ctx = document
    .getElementById("historical-weather-chart")
    .getContext("2d");

  const filePrefix = "/static/data/weather_data/weather_20250302_";
  const fileNames = [];

  // 假设你有 24 份文件，从 000000 到 230000
  for (let h = 0; h < 24; h++) {
    const hh = h.toString().padStart(2, "0");
    fileNames.push(`${filePrefix}${hh}0000.json`);
  }

  const entries = [];

  for (const file of fileNames) {
    try {
      const res = await fetch(file);
      const json = await res.json();
      const entry = json.hourly[0];
      if (entry) entries.push(entry);
    } catch (err) {
      console.warn("⚠️ Skipped:", file);
    }
  }

  // 构建 labels & datasets
  const labels = entries.map((e) =>
    new Date(e.dt * 1000).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    })
  );
  const temps = entries.map((e) => e.temp);
  const windSpeeds = entries.map((e) => `${e.wind_speed.toFixed(1)}m/s`);
  const descriptions = entries.map((e) => e.weather[0].description);

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Temperature (°C)",
          data: temps,
          borderColor: "#e74c3c",
          backgroundColor: "rgba(231, 76, 60, 0.2)",
          tension: 0.3,
          pointRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            title: (ctx) => labels[ctx[0].dataIndex],
            label: (ctx) => [
              `🌡 Temp: ${temps[ctx.dataIndex]}°C`,
              `🌬 Wind: ${windSpeeds[ctx.dataIndex]}`,
              `☁️ Weather: ${descriptions[ctx.dataIndex]}`,
            ],
          },
        },
        legend: { display: false },
        title: {
          display: true,
          text: "Historical weather (1 Day)",
          font: { size: 16 },
        },
      },
      scales: {
        x: {
          ticks: {
            callback: (val, index) => [
              labels[index],
              descriptions[index],
              windSpeeds[index],
            ],
            maxRotation: 0,
            minRotation: 0,
            maxTicksLimit: 12,
          },
        },
        y: {
          title: {
            display: true,
            text: "Temperature (°C)",
          },
        },
      },
    },
  });
};
