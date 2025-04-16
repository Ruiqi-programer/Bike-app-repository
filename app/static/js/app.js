// app.js
import {
  loadStationsForSelect,
  loadMapAndStations,
  setupFilters,
  predict,
  setupPredictionModal,
} from "./map.js";
import { fetchWeather, setupWeatherModal } from "./weather.js";

document.addEventListener("DOMContentLoaded", () => {
  setupFilters();
  fetchWeather();
  setupWeatherModal();
  setupPredictionModal();
  loadStationsForSelect();

  const predictBtn = document.querySelector("#predict-btn");
  if (predictBtn) {
    predictBtn.addEventListener("click", predict);
  }

  const filterBtn = document.getElementById("filter-toggle-btn");
  const dropdown = document.getElementById("filter-dropdown");

  if (filterBtn && dropdown) {
    filterBtn.addEventListener("click", () => {
      dropdown.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
      if (!filterBtn.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add("hidden");
      }
    });
  }

  const searchGroup = document.querySelector(".search-group");
  const searchInput = document.getElementById("station-search");
  const searchIcon = document.querySelector(".search-group i");

  if (searchGroup && searchInput && searchIcon) {
    // Highlight when input or icon is clicked
    searchInput.addEventListener("focus", () => {
      searchGroup.classList.add("active");
    });
    searchIcon.addEventListener("click", () => {
      searchGroup.classList.add("active");
      searchInput.focus(); // Optional: also focus input when icon is clicked
    });

    // Remove highlight when clicking outside
    document.addEventListener("click", (e) => {
      if (!searchGroup.contains(e.target)) {
        searchGroup.classList.remove("active");
      }
    });
  }

  // Create a fixed weather information display area
  function createFixedWeatherDisplay() {
    // Create a container for weather information
    const fixedWeatherContainer = document.createElement('div');
    fixedWeatherContainer.id = 'fixed-weather-container';
    fixedWeatherContainer.className = 'fixed-weather-container';

    // Initialize weather display content - put Current Weather at the top
    fixedWeatherContainer.innerHTML = `
      <div class="fixed-weather-content">
        <p class="weather-title"><strong>Current Weather</strong></p>
        <div id="fixed-weather-info">
          <p><strong>🌡️ Temperature:</strong> --°C</p>
          <p><strong>🤗 Feels Like:</strong> --°C</p>
          <p><strong>💧 Humidity:</strong> --%</p>
          <p><strong>🌬️ Wind:</strong> -- km/h</p>
          <p><strong>☁️ Clouds:</strong> --%</p>
        </div>
      </div>
    `;
    
    // Adds the container to the specified location on the page
    const mapFilters = document.getElementById('map-filters');
    if (mapFilters) {
      mapFilters.appendChild(fixedWeatherContainer);
    }

    // Update the fixed weather information
    updateFixedWeatherDisplay();
  }

  // Update fixed weather display function
  function updateFixedWeatherDisplay() {
    
    // get the current weather data
    fetch("/api/weather")
      .then(res => res.json())
      .then(data => {
        if (!data.current) return;
        
        // update the weather information in the fixed weather display
        const weatherInfoContainer = document.getElementById('fixed-weather-info');
        if (weatherInfoContainer) {
          weatherInfoContainer.innerHTML = `
            <p><strong>🌡️ Temperature:</strong> ${data.current.temp}°C</p>
            <p><strong>🤗 Feels Like:</strong> ${data.current.feels_like}°C</p>
            <p><strong>💧 Humidity:</strong> ${data.current.humidity}%</p>
            <p><strong>🌬️ Wind:</strong> ${data.current.wind_speed} km/h</p>
            <p><strong>☁️ Clouds:</strong> ${data.current.clouds}%</p>
          `;
        }
      })
      .catch(e => console.error("Fixed weather display error:", e));
  }

  // call the createFixedWeatherDisplay function to create the fixed weather display
  createFixedWeatherDisplay();

  // update the fixed weather information every 5 minutes (300000 ms)
  setInterval(updateFixedWeatherDisplay, 300000);
});

// Google Maps init callback
window.initMap = () => {
  console.log("🗺️ Google Maps API loaded");
  loadMapAndStations();
};

window.onload = initMap;

// Load Google Charts
google.charts.load("current", { packages: ["corechart"] });
