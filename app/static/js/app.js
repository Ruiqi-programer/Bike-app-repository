// app.js
import { loadMapAndStations, setupFilters, predict,setupPredictionModal } from "./map.js";
import { fetchWeather, setupWeatherModal } from "./weather.js";

document.addEventListener("DOMContentLoaded", () => {
  setupFilters();
  fetchWeather();
  setupWeatherModal();
  setupPredictionModal();

  const predictBtn = document.querySelector("#predict-btn");
  if (predictBtn) {
    predictBtn.addEventListener("click", predict);
  }
});


window.initMap = () => {
  console.log("🗺️ Google Maps API loaded");
  loadMapAndStations();
};

window.onload = initMap;

google.charts.load("current", { packages: ["corechart"] });
