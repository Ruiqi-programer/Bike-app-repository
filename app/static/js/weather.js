// weather.js
let hourlyDataCache = [];

export function fetchWeather() {
  fetch("/api/weather")
    .then((res) => res.json())
    .then((data) => {
      if (!data.current) return;
      showCurrentWeather(data.current);
      hourlyDataCache = data.hourly || [];
    })
    .catch((e) => console.error("Weather fetch error:", e));
}

export function setupWeatherModal() {
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

  window.addEventListener("click", (e) => {
    if (e.target === weatherModal) weatherModal.style.display = "none";
  });
}

function showCurrentWeather(current) {
  const container = document.getElementById("current-weather-info");
  if (!container) return;

  container.innerHTML = `
    <p>🌡️ Temp: ${current.temp}°C</p>
    <p>💧 Humidity: ${current.humidity}%</p>
    <p>🌬️ Wind: ${current.wind_speed} km/h</p>
    <p>☁️ Clouds: ${current.clouds}%</p>
  `;
}

function drawHourlyChart() {
  const ctx = document.getElementById("hourly-temp-chart")?.getContext("2d");
  if (!ctx || !hourlyDataCache.length) return;

  const labels = hourlyDataCache.map((h) =>
    new Date(h.dt).toLocaleTimeString([], { hour: "2-digit", hour12: true })
  );
  const temps = hourlyDataCache.map((h) => h.temp);

  if (window.hourlyChart) window.hourlyChart.destroy();

  window.hourlyChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Temperature (°C)",
          data: temps,
          borderColor: "#ff6384",
          backgroundColor: "rgba(255,99,132,0.1)",
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: false },
      },
    },
  });
}
