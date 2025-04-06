// map.js
let map;
let markers = [];
let currentInfoWindow = null;

const activeFilters = {
  search: "",
  hasBikes: false,
  hasStands: false,
  notEmpty: false,
  notFull: false,
};

export function loadMapAndStations() {
  const mapElement = document.getElementById("map");
  if (!mapElement) {
    console.error("Map element not found!");
    return;
  }

  map = new google.maps.Map(mapElement, {
    center: { lat: 53.349805, lng: -6.26031 },
    zoom: 13,
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
  if (loadingEl) loadingEl.style.display = "block";

  fetch("/api/stations")
    .then((response) => response.json())
    .then((data) => {
      clearMarkers();
      if (!Array.isArray(data)) return;

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
                 <p>Total Stands: ${station.total_bike_stands}</p>
                <div id="chart_div_${station.station_id}" class="station-chart"></div>
              </div>
          `,
        });

        marker.addListener("gmp-click", () => {
          // 关闭之前打开的 InfoWindow
          if (currentInfoWindow) {
            currentInfoWindow.close();
          }
          // 打开当前 InfoWindow
          map.panTo(marker.position);
          smoothZoom(map, 17);
          infoWindow.open(map, marker);

          // 保存当前窗口引用
          currentInfoWindow = infoWindow;

          google.charts.setOnLoadCallback(() => {
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
        });

        markers.push(marker);
      });
    })
    .catch((err) => console.error("❌ Failed to load stations", err))
    .finally(() => {
      if (loadingEl) loadingEl.style.display = "none";
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
