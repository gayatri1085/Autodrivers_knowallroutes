/**
 * AutoRouteAI API client
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE_URL}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  /**
   * Get AI-ranked routes between two points.
   * @param {Object} params - { origin, destination, city, preferences }
   */
  getRoutes(params) {
    return apiFetch("/route", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Geocode a search query within a city.
   */
  search(query, city = "chennai") {
    return apiFetch(`/search?q=${encodeURIComponent(query)}&city=${city}`);
  },

  /**
   * Get traffic prediction for a location.
   */
  getTraffic(lat, lng, city = "chennai", horizonMinutes = 30) {
    return apiFetch(`/traffic?lat=${lat}&lng=${lng}&city=${city}&horizon_minutes=${horizonMinutes}`);
  },

  /**
   * Analyse sentiment of driver feedback text.
   */
  analyseSentiment(text, language = "en") {
    return apiFetch("/sentiment", {
      method: "POST",
      body: JSON.stringify({ text, language }),
    });
  },

  /**
   * Get road quality score for an OSM way ID.
   */
  getRoadScore(wayId) {
    return apiFetch(`/road_score?way_id=${wayId}`);
  },

  /**
   * Submit route feedback.
   */
  submitFeedback(routeId, rating, comment, city) {
    return apiFetch("/feedback", {
      method: "POST",
      body: JSON.stringify({ route_id: routeId, rating, comment, city }),
    });
  },

  /**
   * Get weather and flood risk.
   */
  getWeather(lat, lng) {
    return apiFetch(`/weather?lat=${lat}&lng=${lng}`);
  },
};
