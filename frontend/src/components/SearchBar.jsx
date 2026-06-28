import { useState, useRef } from "react";
import { Search, MapPin, Navigation, X } from "lucide-react";
import { api } from "../services/api";

export default function SearchBar({ city, onOriginSet, onDestinationSet, onSearch }) {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [originSuggestions, setOriginSuggestions] = useState([]);
  const [destSuggestions, setDestSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef(null);

  const suggest = async (query, setSuggestions) => {
    if (query.length < 3) { setSuggestions([]); return; }
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      try {
        const results = await api.search(query, city);
        setSuggestions(results.slice(0, 5));
      } catch {
        setSuggestions([]);
      }
    }, 350);
  };

  const handleOriginChange = (e) => {
    setOrigin(e.target.value);
    suggest(e.target.value, setOriginSuggestions);
  };

  const handleDestChange = (e) => {
    setDestination(e.target.value);
    suggest(e.target.value, setDestSuggestions);
  };

  const pickOrigin = (item) => {
    setOrigin(item.display_name.split(",")[0]);
    setOriginSuggestions([]);
    onOriginSet({ lat: item.lat, lng: item.lng, name: item.display_name });
  };

  const pickDest = (item) => {
    setDestination(item.display_name.split(",")[0]);
    setDestSuggestions([]);
    onDestinationSet({ lat: item.lat, lng: item.lng, name: item.display_name });
  };

  const handleGo = async () => {
    setLoading(true);
    try {
      await onSearch();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-bar">
      <div className="search-field-group">
        {/* Origin */}
        <div className="search-field">
          <MapPin size={16} className="field-icon origin" />
          <input
            type="text"
            placeholder="Starting point"
            value={origin}
            onChange={handleOriginChange}
          />
          {origin && (
            <button className="clear-btn" onClick={() => { setOrigin(""); setOriginSuggestions([]); }}>
              <X size={14} />
            </button>
          )}
        </div>
        {originSuggestions.length > 0 && (
          <ul className="suggestions">
            {originSuggestions.map((s, i) => (
              <li key={i} onClick={() => pickOrigin(s)}>
                <MapPin size={12} />
                <span>{s.display_name.split(",").slice(0, 2).join(", ")}</span>
              </li>
            ))}
          </ul>
        )}

        <div className="field-divider" />

        {/* Destination */}
        <div className="search-field">
          <Navigation size={16} className="field-icon dest" />
          <input
            type="text"
            placeholder="Where to?"
            value={destination}
            onChange={handleDestChange}
          />
          {destination && (
            <button className="clear-btn" onClick={() => { setDestination(""); setDestSuggestions([]); }}>
              <X size={14} />
            </button>
          )}
        </div>
        {destSuggestions.length > 0 && (
          <ul className="suggestions">
            {destSuggestions.map((s, i) => (
              <li key={i} onClick={() => pickDest(s)}>
                <Navigation size={12} />
                <span>{s.display_name.split(",").slice(0, 2).join(", ")}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <button className="go-btn" onClick={handleGo} disabled={loading}>
        {loading ? (
          <span className="spinner" />
        ) : (
          <>
            <Search size={16} />
            Get Routes
          </>
        )}
      </button>
    </div>
  );
}
