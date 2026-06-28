import { Clock, Ruler, Star, Shield, TrendingUp, ChevronRight, ThumbsUp, ThumbsDown } from "lucide-react";
import { api } from "../services/api";

function ScoreBar({ value, color }) {
  return (
    <div className="score-bar-track">
      <div
        className="score-bar-fill"
        style={{ width: `${Math.round(value * 100)}%`, background: color }}
      />
    </div>
  );
}

function ScorePill({ label, value, icon: Icon, color }) {
  const pct = Math.round(value * 100);
  return (
    <div className="score-pill">
      <Icon size={12} />
      <span className="score-label">{label}</span>
      <ScoreBar value={value} color={color} />
      <span className="score-value">{pct}%</span>
    </div>
  );
}

export default function RouteCard({ route, isSelected, onSelect, city }) {
  const isRecommended = route.label === "Driver Recommended";

  const handleFeedback = async (thumbs) => {
    try {
      await api.submitFeedback(route.route_id, thumbs === "up" ? 5 : 1, null, city);
    } catch { /* silent */ }
  };

  return (
    <div
      className={`route-card ${isSelected ? "selected" : ""} ${isRecommended ? "recommended" : ""}`}
      onClick={onSelect}
    >
      {isRecommended && (
        <div className="recommended-badge">
          <Star size={11} fill="currentColor" />
          Driver Pick
        </div>
      )}

      <div className="route-card-header">
        <div className="route-label">{route.label}</div>
        <ChevronRight size={16} className="chevron" />
      </div>

      <div className="route-meta">
        <span className="meta-item">
          <Clock size={13} />
          {route.eta_minutes} min
        </span>
        <span className="meta-item">
          <Ruler size={13} />
          {route.distance_km} km
        </span>
      </div>

      <div className="route-scores">
        <ScorePill label="Road" value={route.road_quality_score} icon={TrendingUp} color="#22c55e" />
        <ScorePill label="Safety" value={route.safety_score} icon={Shield} color="#3b82f6" />
        <ScorePill label="Driver" value={route.driver_score} icon={Star} color="#f59e0b" />
      </div>

      {route.highlights.length > 0 && (
        <ul className="route-highlights">
          {route.highlights.map((h, i) => (
            <li key={i}>· {h}</li>
          ))}
        </ul>
      )}

      <div className="route-feedback">
        <span className="feedback-label">Helpful?</span>
        <button className="feedback-btn" onClick={(e) => { e.stopPropagation(); handleFeedback("up"); }}>
          <ThumbsUp size={13} />
        </button>
        <button className="feedback-btn" onClick={(e) => { e.stopPropagation(); handleFeedback("down"); }}>
          <ThumbsDown size={13} />
        </button>
      </div>
    </div>
  );
}
