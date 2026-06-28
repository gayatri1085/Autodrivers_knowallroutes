import { useEffect, useRef } from "react";

// MapLibre GL JS is loaded via CDN in index.html for simplicity
// In a real build, import from 'maplibre-gl'

const CITY_CENTERS = {
  chennai:   { lat: 13.0827, lng: 80.2707, zoom: 12 },
  bengaluru: { lat: 12.9716, lng: 77.5946, zoom: 12 },
  hyderabad: { lat: 17.3850, lng: 78.4867, zoom: 12 },
  kochi:     { lat: 9.9312,  lng: 76.2673, zoom: 12 },
};

const ROUTE_COLORS = ["#f59e0b", "#3b82f6", "#6b7280"];

export default function MapView({ routes, selectedRoute, city, origin, destination }) {
  const mapRef      = useRef(null);
  const mapInstance = useRef(null);

  useEffect(() => {
    if (!window.maplibregl || mapInstance.current) return;

    const center = CITY_CENTERS[city] || CITY_CENTERS.chennai;
    const map = new window.maplibregl.Map({
      container: mapRef.current,
      style: "https://tiles.openfreemap.org/styles/liberty",
      center: [center.lng, center.lat],
      zoom: center.zoom,
    });

    map.addControl(new window.maplibregl.NavigationControl(), "top-right");
    mapInstance.current = map;

    return () => {
      map.remove();
      mapInstance.current = null;
    };
  }, []);

  // Fly to city on change
  useEffect(() => {
    const map = mapInstance.current;
    if (!map) return;
    const center = CITY_CENTERS[city] || CITY_CENTERS.chennai;
    map.flyTo({ center: [center.lng, center.lat], zoom: 12, duration: 1200 });
  }, [city]);

  // Draw routes
  useEffect(() => {
    const map = mapInstance.current;
    if (!map || routes.length === 0) return;

    const draw = () => {
      // Remove old layers/sources
      for (let i = 0; i < 3; i++) {
        if (map.getLayer(`route-${i}`)) map.removeLayer(`route-${i}`);
        if (map.getSource(`route-${i}`)) map.removeSource(`route-${i}`);
      }
      if (map.getLayer("origin-marker")) map.removeLayer("origin-marker");
      if (map.getSource("origin-source")) map.removeSource("origin-source");
      if (map.getLayer("dest-marker")) map.removeLayer("dest-marker");
      if (map.getSource("dest-source")) map.removeSource("dest-source");

      // Draw routes (selected last so it's on top)
      const ordered = [...routes].sort((a) =>
        a.route_id === selectedRoute?.route_id ? 1 : -1
      );

      ordered.forEach((route, idx) => {
        const originalIdx = routes.indexOf(route);
        const isSelected = route.route_id === selectedRoute?.route_id;
        const id = `route-${originalIdx}`;
        map.addSource(id, {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: { type: "LineString", coordinates: route.geometry },
            properties: {},
          },
        });
        map.addLayer({
          id,
          type: "line",
          source: id,
          layout: { "line-join": "round", "line-cap": "round" },
          paint: {
            "line-color": isSelected ? ROUTE_COLORS[0] : ROUTE_COLORS[originalIdx] || "#9ca3af",
            "line-width": isSelected ? 5 : 3,
            "line-opacity": isSelected ? 1 : 0.5,
          },
        });
      });

      // Origin marker
      if (origin) {
        map.addSource("origin-source", {
          type: "geojson",
          data: { type: "Feature", geometry: { type: "Point", coordinates: [origin.lng, origin.lat] } },
        });
        map.addLayer({
          id: "origin-marker",
          type: "circle",
          source: "origin-source",
          paint: { "circle-radius": 8, "circle-color": "#22c55e", "circle-stroke-width": 2, "circle-stroke-color": "#fff" },
        });
      }

      // Destination marker
      if (destination) {
        map.addSource("dest-source", {
          type: "geojson",
          data: { type: "Feature", geometry: { type: "Point", coordinates: [destination.lng, destination.lat] } },
        });
        map.addLayer({
          id: "dest-marker",
          type: "circle",
          source: "dest-source",
          paint: { "circle-radius": 8, "circle-color": "#ef4444", "circle-stroke-width": 2, "circle-stroke-color": "#fff" },
        });
      }

      // Fit bounds to first route
      if (routes[0]?.geometry?.length > 0) {
        const coords = routes[0].geometry;
        const lngs = coords.map(c => c[0]);
        const lats = coords.map(c => c[1]);
        map.fitBounds(
          [[Math.min(...lngs), Math.min(...lats)], [Math.max(...lngs), Math.max(...lats)]],
          { padding: 60, duration: 800 }
        );
      }
    };

    if (map.isStyleLoaded()) {
      draw();
    } else {
      map.once("load", draw);
    }
  }, [routes, selectedRoute, origin, destination]);

  return (
    <div className="map-container">
      <div ref={mapRef} className="map" />
      <div className="map-attribution">
        © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors
      </div>
    </div>
  );
}
