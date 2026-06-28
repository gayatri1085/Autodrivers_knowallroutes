import { Moon, Sun, MapPin } from "lucide-react";

const CITIES = [
  { id: "chennai",   label: "Chennai" },
  { id: "bengaluru", label: "Bengaluru" },
  { id: "hyderabad", label: "Hyderabad" },
  { id: "kochi",     label: "Kochi" },
];

export default function Settings({ city, onCityChange, darkMode, onToggleDarkMode }) {
  return (
    <div className="settings-panel">
      <div className="settings-section">
        <h3 className="settings-title">
          <MapPin size={14} />
          City
        </h3>
        <div className="city-grid">
          {CITIES.map((c) => (
            <button
              key={c.id}
              className={`city-btn ${city === c.id ? "active" : ""}`}
              onClick={() => onCityChange(c.id)}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      <div className="settings-section">
        <h3 className="settings-title">Appearance</h3>
        <button className="dark-mode-toggle" onClick={onToggleDarkMode}>
          {darkMode ? <Sun size={15} /> : <Moon size={15} />}
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </div>

      <div className="settings-section">
        <h3 className="settings-title">About</h3>
        <p className="settings-about">
          AutoRouteAI encodes local auto driver knowledge into AI-powered navigation
          for South Indian cities. Routes are scored on road quality, driver sentiment,
          safety, and real-time traffic — not just distance.
        </p>
        <div className="settings-links">
          <a href="https://github.com/yourusername/AutoRouteAI" target="_blank" rel="noreferrer">
            GitHub →
          </a>
        </div>
      </div>
    </div>
  );
}
