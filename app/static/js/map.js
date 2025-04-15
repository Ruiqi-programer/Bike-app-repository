// map.js
let map;
let markers = [];
let currentInfoWindow = null;
let predictionChart = null;
let historicalWeatherChartInstance = null;
let filteredStations = [];
let stationDataMap = {};

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
    mapId: "8adf177586ed1224",
    gestureHandling: "greedy",
    mapTypeControl: true,
    zoomControl: true,
    streetViewControl: true,
    fullscreenControl: true,
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

  search.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && filteredStations.length === 1) {
      const { marker, infoWindow } = filteredStations[0];

      if (currentInfoWindow) currentInfoWindow.close();

      map.panTo(marker.position);

      infoWindow.open(map, marker);
      currentInfoWindow = infoWindow;

      infoWindow.addListener("domready", () => {
        InfoWindowEvents(filteredStations[0].station);
      });
    }
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

      filteredStations = [];
      data.forEach((station) => {
        const searchWords = activeFilters.search
          .trim()
          .toLowerCase()
          .split(/\s+/);
        const stationWords =
          station.name.toLowerCase().match(/\b[a-z]+\b/g) || [];

        let usedIndexes = new Set();
        let nameMatch = true;

        for (let i = 0; i < searchWords.length; i++) {
          const searchWord = searchWords[i];
          const isLastWord = i === searchWords.length - 1;

          let matched = false;

          for (let j = 0; j < stationWords.length; j++) {
            const stationWord = stationWords[j];

            // 若未被匹配，进行匹配检查
            if (!usedIndexes.has(j)) {
              const isFullMatch = stationWord === searchWord;
              const isPrefixMatch = stationWord.startsWith(searchWord);

              if ((isLastWord && isPrefixMatch) || isFullMatch) {
                usedIndexes.add(j);
                matched = true;
                break;
              }
            }
          }

          if (!matched) {
            nameMatch = false;
            break;
          }
        }
        const hasBikes = station.available_bikes > 0;
        const hasStands = station.available_bike_stands > 0;
        const isFullyUnavailable =
          station.available_bikes === 0 && station.available_bike_stands === 0;

        if (
          (activeFilters.search && !nameMatch) ||
          (activeFilters.hasBikes && !hasBikes) ||
          (activeFilters.hasStands && !hasStands) ||
          (activeFilters.notEmpty && station.available_bikes !== 0) ||
          (activeFilters.notFull &&
            (station.available_bike_stands !== 0 || isFullyUnavailable))
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
        marker.content.addEventListener("mouseenter", () => {
          if (!marker.content.dataset.promoted) {
            marker.map = null;
            marker.map = map;
            marker.content.dataset.promoted = "true";
          }
        });

        marker.content.addEventListener("mouseleave", () => {
          delete marker.content.dataset.promoted;
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
            InfoWindowEvents(station);
          });
        });

        filteredStations.push({ station, marker, infoWindow });
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

function InfoWindowEvents(station) {
  const chartElement = document.getElementById(
    `chart_div_${station.station_id}`
  );
  if (chartElement) {
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
      colors: ["#bdc3c7", "#dfe6e9"],
    });
  }

  setTimeout(() => {
    const predictionBtn = document.getElementById("view-prediction-btn");

    predictionBtn.addEventListener("click", () => {
      const sid = predictionBtn.dataset.stationId;
      const name = predictionBtn.dataset.stationName;
      window.showPredictionChart(sid, name);
      window.drawHistoricalBikeChart(sid);
      window.drawHistoricalWeatherChart();
    });
  });
}

function clearMarkers() {
  markers.forEach((marker) => marker.setMap(null));
  markers = [];
}

function createMarkerIcon(color, count) {
  // const el = document.createElement("div");
  // el.className = "custom-marker";
  // el.style.background = color;
  // el.style.border = "2px solid black";
  // el.style.borderRadius = "50%";
  // el.style.width = "32px";
  // el.style.height = "32px";
  // el.style.display = "flex";
  // el.style.alignItems = "center";
  // el.style.justifyContent = "center";
  // el.style.fontWeight = "bold";
  // el.style.color = "white";
  // el.innerText = count;
  const el = document.createElement("div");
  el.className = "custom-teardrop-marker";

  // 设置颜色
  el.style.setProperty("--pin-color", color);

  // 设置文字内容
  const inner = document.createElement("div");
  inner.className = "marker-count";
  inner.textContent = count;
  el.appendChild(inner);

  el.addEventListener("mouseenter", () => {
    el.style.zIndex = "9999";
  });

  el.addEventListener("mouseleave", () => {
    el.style.zIndex = "1";
  });

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
        const predictedBikes = data.predicted_available_bikes;
        const totalStands = stationDataMap[stationId];
        const predictedStands =
          typeof totalStands === "number"
            ? totalStands - predictedBikes
            : "N/A";
        resultDiv.innerHTML = `<div class="prediction-line">🚲 Predicted Bikes: <strong>${predictedBikes}</strong></div>
  <div class="prediction-line">🅿️ Predicted Free Stands: <strong>${predictedStands}</strong></div>
  <div class="prediction-line">🔢 Total Stands: <strong>${
    totalStands ?? "N/A"
  }</strong></div>`;
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

        stationDataMap[station.station_id] = station.total_bike_stands;
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
  const freeStands = [];
  const labels = [];
  let fetches = [];

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
          const bikes = data.predicted_available_bikes ?? 0;
          const totalStands = stationDataMap[stationId] ?? 0;
          const stands = totalStands - bikes;
          return { bikes, stands };
        } else {
          console.error("Fetch error:", err);
          return { bikes: 0, stands: 0 };
        }
      })
      .catch((err) => {
        console.error("Prediction fetch error:", err);
        return 0;
      });

    fetches.push(fetchPromise);
  }

  Promise.all(fetches).then((predictions) => {
    const predictedBikes = predictions.map((r) => r.bikes);
    const predictedStands = predictions.map((r) => r.stands);

    updatePredictionChart(labels, predictedBikes, predictedStands);
  });
};

function updatePredictionChart(labels, predictions, freeStands) {
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
          fill: false,
          tension: 0.4,
        },
        {
          label: "Predicted Free Stands",
          data: freeStands,
          borderColor: "#f39c12",
          backgroundColor: "rgba(243, 156, 18, 0.2)",
          fill: false,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,

      layout: {
        padding: {
          left: 10, // ✅ 给 Y轴留出空间
          right: 10,
          top: 10,
          bottom: 10,
        },
      },
      scales: {
        x: {
          title: { display: true, text: "Time (Hour)" },
        },
        y: {
          title: { display: true, text: "Count" },
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

    const now = new Date();

    const dateInput = document.getElementById("predict-date");
    const timeInput = document.getElementById("predict-time");

    // 设置最小日期为今天
    dateInput.min = now.toISOString().split("T")[0];
    dateInput.value = now.toISOString().split("T")[0];

    // 设置最小时间为当前时间（仅当天有效）
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    timeInput.min = `${hours}:${minutes}`;
    timeInput.value = `${hours}:${minutes}`;

    // 如果用户改日期，时间应恢复为00:00（除非是今天）
    dateInput.addEventListener("change", () => {
      const selectedDate = dateInput.value;
      const today = now.toISOString().split("T")[0];
      if (selectedDate !== today) {
        timeInput.min = "00:00";
        timeInput.value = "08:00"; // 你可设定一个默认值
      } else {
        timeInput.min = `${hours}:${minutes}`;
        timeInput.value = `${hours}:${minutes}`;
      }
    });
  });

  closeModal.addEventListener("click", () => {
    predictionModal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === predictionModal) predictionModal.style.display = "none";
  });
}

/* historical bike data */
window.drawHistoricalBikeChart = async function (stationId) {
  const ctx = document
    .getElementById("historical-bike-chart")
    ?.getContext("2d");
  if (!ctx) return;

  const csvUrl = "/static/data/merged_bike_data.csv";
  const response = await fetch(csvUrl);
  const csvText = await response.text();

  const rows = csvText.trim().split("\n");
  const headers = rows[0].split(",");

  const data = rows
    .slice(1)
    .map((row) => {
      const values = row.split(",");
      const entry = {};
      headers.forEach((h, i) => {
        entry[h] = values[i];
      });
      return entry;
    })
    .filter((d) => parseInt(d.number) === parseInt(stationId))
    .map((d) => ({
      time: new Date(parseInt(d.last_update)),
      bikes: parseInt(d.available_bikes),
      stands: parseInt(d.available_bike_stands),
    }))
    .sort((a, b) => a.time - b.time);

  const labels = data.map((d) =>
    d.time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  );
  const bikes = data.map((d) => d.bikes);
  const stands = data.map((d) => d.stands);

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
          pointRadius: 0,
        },
        {
          label: "Available Stands",
          data: stands,
          borderColor: "#3498db",
          backgroundColor: "rgba(52, 152, 219, 0.2)",
          tension: 0.3,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      layout: {
        padding: {
          left: 10, // ✅ 给 Y轴留出空间
          right: 10,
          top: 10,
          bottom: 10,
        },
      },
      plugins: {
        title: {
          display: true,
          text: "Historical Bike Availability",
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

  const csvUrl = "/static/data/merged_current_weather.csv";
  const res = await fetch(csvUrl);
  const csvText = await res.text();

  const rows = csvText.trim().split("\n");
  const headers = rows[0].split(",");

  const data = rows.slice(1).map((row) => {
    const values = row.split(",");
    const obj = {};
    headers.forEach((h, i) => (obj[h] = values[i]));
    return obj;
  });

  // 提取字段
  const labels = data.map((d) =>
    new Date(d.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    })
  );
  const temps = data.map((d) => parseFloat(d.temp));
  const humidity = data.map((d) => parseFloat(d.humidity));
  const windSpeed = data.map((d) => parseFloat(d.wind_speed));
  const descriptions = data.map((d) => d.weather_main);
  if (historicalWeatherChartInstance) {
    historicalWeatherChartInstance.destroy();
  }
  new Chart(ctx, {
    type: "line", // 可改为 'bar'
    data: {
      labels,
      datasets: [
        {
          label: "Temperature (°C)",
          data: temps,
          borderColor: "#e67e22",
          backgroundColor: "rgba(230, 126, 34, 0.2)",
          tension: 0.3,
          pointRadius: 3,
          yAxisID: "y",
        },
        {
          label: "Humidity (%)",
          data: humidity,
          borderColor: "#3498db",
          backgroundColor: "rgba(52, 152, 219, 0.2)",
          tension: 0.3,
          pointRadius: 3,
          yAxisID: "y1",
        },
      ],
    },
    options: {
      responsive: true,
      layout: {
        padding: {
          left: 10, // ✅ 给 Y轴留出空间
          right: 10,
          top: 10,
          bottom: 10,
        },
      },
      interaction: { mode: "index", intersect: false },
      stacked: false,
      plugins: {
        title: {
          display: true,
          text: "Historical Weather",
          font: { size: 16 },
        },
        tooltip: {
          callbacks: {
            label: () => null,
            title: (ctx) => labels[ctx[0].dataIndex],
            afterLabel: (ctx) => {
              const i = ctx.dataIndex;
              if (ctx.datasetIndex !== 0) return "";
              return [
                `🌡 Temp: ${temps[i]}°C`,
                `💧 Humidity: ${humidity[i]}%`,
                `🌬 Wind: ${windSpeed[i]} m/s`,
                `☁️ Weather: ${descriptions[i]}`,
              ];
            },
          },
        },
      },
      scales: {
        x: { title: { display: true, text: "Time" } },
        y: {
          type: "linear",
          display: true,
          position: "left",
          title: { display: true, text: "Temperature (°C)" },
        },
        y1: {
          type: "linear",
          display: true,
          position: "right",
          grid: { drawOnChartArea: false },
          title: { display: true, text: "Humidity (%)" },
        },
      },
    },
  });
};
