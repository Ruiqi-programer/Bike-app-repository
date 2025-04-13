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
    // 当点击输入框或图标时激活高亮
    searchInput.addEventListener("focus", () => {
      searchGroup.classList.add("active");
    });
    searchIcon.addEventListener("click", () => {
      searchGroup.classList.add("active");
      searchInput.focus(); // 可选：点击图标也聚焦输入框
    });

    // 当点击页面其他地方时，移除高亮
    document.addEventListener("click", (e) => {
      if (!searchGroup.contains(e.target)) {
        searchGroup.classList.remove("active");
      }
    });
  }
});

window.initMap = () => {
  console.log("🗺️ Google Maps API loaded");
  loadMapAndStations();
};

window.onload = initMap;

google.charts.load("current", { packages: ["corechart"] });
