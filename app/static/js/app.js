// app.js
import { loadMapAndStations, setupFilters } from "./map.js";
import { fetchWeather, setupWeatherModal } from "./weather.js";

document.addEventListener("DOMContentLoaded", () => {
  setupFilters();
  fetchWeather();
  setupWeatherModal();
});

window.initMap = () => {
  console.log("🗺️ Google Maps API loaded");
  loadMapAndStations();
};

google.charts.load("current", { packages: ["corechart"] });
