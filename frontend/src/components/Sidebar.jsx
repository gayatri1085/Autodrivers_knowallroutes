import { useState } from "react";
import { Map, List, Settings as SettingsIcon, MessageSquare } from "lucide-react";
import RouteCard from "./RouteCard";
import DriverInsights from "./DriverInsights";
import Settings from "./Settings";

const TABS = [
  { id: "routes",   label: "Routes",   Icon: List },
  { id: "insights", label: "Insights", Icon: MessageSquare },
  { id: "settings", label: "Settings", Icon: SettingsIcon },
];

export default function Sidebar({
  routes,
  selectedRoute,
  onSelectRoute,
  city,
  onCityChange,
  darkMode,
  onToggleDarkMode,
}) {
  const [tab, setTab] = useState("routes");

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand">
          <span className="brand-icon">🚖</span>
          <div>
            <h1 className="brand-name">AutoRoute<span className="brand-ai">AI</span></h1>
            <p className="brand-tagline">Knows every road like a local</p>
          </div>
        </div>
      </div>

      <nav className="sidebar-tabs">
        {TABS.map(({ id, label, Icon }) => (
          <button
            key={id}
            className={`tab-btn ${tab === id ? "active" : ""}`}
            onClick={() => setTab(id)}
          >
            <Icon size={15} />
            {label}
          </button>
        ))}
      </nav>

      <div className="sidebar-content">
        {tab === "routes" && (
          <div className="routes-panel">
            {routes.length === 0 ? (
              <div className="empty-state">
                <Map size={32} className="empty-icon" />
                <p>Search a destination to see AI-ranked routes from an auto driver's perspective.</p>
              </div>
            ) : (
              routes.map((route) => (
                <RouteCard
                  key={route.route_id}
                  route={route}
                  isSelected={selectedRoute?.route_id === route.route_id}
                  onSelect={() => onSelectRoute(route)}
                  city={city}
                />
              ))
            )}
          </div>
        )}

        {tab === "insights" && (
          <DriverInsights city={city} selectedRoute={selectedRoute} />
        )}

        {tab === "settings" && (
          <Settings
            city={city}
            onCityChange={onCityChange}
            darkMode={darkMode}
            onToggleDarkMode={onToggleDarkMode}
          />
        )}
      </div>
    </aside>
  );
}
