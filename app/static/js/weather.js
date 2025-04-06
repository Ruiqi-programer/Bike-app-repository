// weather.js
let hourlyDataCache = [];

export function fetchWeather() {
  fetch("/api/weather")
    .then((res) => res.json())
    .then((data) => {
      if (!data.current) return;
      showCurrentWeather(data.current);
      hourlyDataCache = data.hourly || [];
      showDailyForecast(data.daily || []);
      showHourlyTimeline(data.hourly || []);
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

  daily.forEach((day) => {
    const date = new Date(day.dt);
    const dateString = date.toLocaleDateString(undefined, {
      weekday: "short",
      month: "short",
      day: "numeric",
    });

    const iconCode = day.weather_icon ?? "";
    const iconUrl = iconCode
      ? `https://openweathermap.org/img/wn/${iconCode}@2x.png`
      : "";
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
          fill: true,
          borderColor: "rgba(255, 99, 132, 1)",
          backgroundColor: "rgba(255, 99, 132, 0.1)",
          tension: 0.4,
          pointRadius: 5,
          pointHoverRadius: 7,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: "12-Hour Temperature Trend",
          font: { size: 18 },
        },
      },
      scales: {
        x: { ticks: { maxRotation: 30, minRotation: 30 } },
        y: {
          beginAtZero: false,
          title: { display: true, text: "Temperature (°C)" },
        },
      },
    },
  });
}

function showHourlyTimeline(hourly) {
  const container = document.getElementById("hourly-timeline");
  if (!container || !Array.isArray(hourly)) return;

  container.innerHTML = "";

  hourly.forEach((hour) => {
    const date = new Date(hour.dt);
    const time = date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
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
