import { useState } from "react";
import Sidebar from "../components/Sidebar";
import SearchBar from "../components/SearchBar";
import MapView from "../components/MapView";
import { api } from "../services/api";

export default function Home({ darkMode, onToggleDarkMode }) {
  const [city, setCity]               = useState("chennai");
  const [origin, setOrigin]           = useState(null);
  const [destination, setDestination] = useState(null);
  const [routes, setRoutes]           = useState([]);
  const [selectedRoute, setSelected]  = useState(null);
  const [error, setError]             = useState(null);

  const handleSearch = async () => {
    if (!origin || !destination) {
      setError("Please set both a starting point and destination.");
      return;
    }
    setError(null);
    try {
      const data = await api.getRoutes({
        origin:      { lat: origin.lat, lng: origin.lng },
        destination: { lat: destination.lat, lng: destination.lng },
        city,
        preferences: { avoid_floods: true, road_quality_weight: 0.3, time_weight: 0.4, driver_score_weight: 0.3 },
      });
      setRoutes(data.routes);
      setSelected(data.routes[0] || null);
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar
        routes={routes}
        selectedRoute={selectedRoute}
        onSelectRoute={setSelected}
        city={city}
        onCityChange={setCity}
        darkMode={darkMode}
        onToggleDarkMode={onToggleDarkMode}
      />

      <main className="map-section">
        <div className="search-overlay">
          <SearchBar
            city={city}
            onOriginSet={setOrigin}
            onDestinationSet={setDestination}
            onSearch={handleSearch}
          />
          {error && <div className="error-toast">{error}</div>}
        </div>

        <MapView
          routes={routes}
          selectedRoute={selectedRoute}
          city={city}
          origin={origin}
          destination={destination}
        />
      </main>
    </div>
  );
}
