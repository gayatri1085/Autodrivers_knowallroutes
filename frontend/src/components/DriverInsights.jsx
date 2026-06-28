import { useState } from "react";
import { MessageSquare, Send, AlertCircle } from "lucide-react";
import { api } from "../services/api";

const SAMPLE_INSIGHTS = {
  chennai: [
    "Anna Salai gets very congested between 5–8 PM. Take Poonamallee High Road instead.",
    "Avoid T. Nagar area on weekends — shopping traffic is unpredictable.",
    "Cathedral Road is smooth but narrow near Gopalapuram during school hours.",
    "ECR is great for speed but avoid it in monsoon — Muttukadu stretch floods fast.",
  ],
  bengaluru: [
    "Outer Ring Road appears fastest but bunches badly near Marathahalli 7–9 AM.",
    "Indiranagar 100 Feet Road is solid — local autos prefer it for reliability.",
    "Silk Board junction — plan 30 extra minutes, always.",
    "Bannerghatta Road after Jayadeva has good surface quality post 2024 repair.",
  ],
  hyderabad: [
    "HITEC City flyover saves 15 min, but merges onto Gachibowli Flyover can be tricky.",
    "Old city roads are narrow — auto drivers know the one-ways that maps don't show.",
    "Tank Bund is scenic and smooth, good alternative to NH65 in off-peak.",
  ],
  kochi: [
    "Edapally Junction — avoid 8–10 AM, pick National Highway only after 10.",
    "Marine Drive route is preferred for comfort, slower but excellent road quality.",
    "Vyttila Mobility Hub area has poor surface — budget extra ETA.",
  ],
};

export default function DriverInsights({ city, selectedRoute }) {
  const [feedbackText, setFeedbackText] = useState("");
  const [sentimentResult, setSentimentResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const insights = SAMPLE_INSIGHTS[city] || SAMPLE_INSIGHTS.chennai;

  const handleAnalyse = async () => {
    if (!feedbackText.trim()) return;
    setSubmitting(true);
    try {
      const result = await api.analyseSentiment(feedbackText);
      setSentimentResult(result);
    } catch {
      setSentimentResult({ label: "neutral", score: 0.5, road_aspects: {} });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="insights-panel">
      <div className="insights-section">
        <h3 className="insights-title">
          <MessageSquare size={14} />
          Local Driver Knowledge — {city.charAt(0).toUpperCase() + city.slice(1)}
        </h3>
        <ul className="insights-list">
          {insights.map((tip, i) => (
            <li key={i} className="insight-item">
              <span className="insight-bullet">🚖</span>
              {tip}
            </li>
          ))}
        </ul>
      </div>

      {selectedRoute && (
        <div className="insights-section">
          <h3 className="insights-title">
            <AlertCircle size={14} />
            Selected Route Analysis
          </h3>
          <div className="route-analysis">
            <div className="analysis-row">
              <span>Road Quality</span>
              <span className={`analysis-val ${selectedRoute.road_quality_score > 0.6 ? "good" : "warn"}`}>
                {Math.round(selectedRoute.road_quality_score * 100)}%
              </span>
            </div>
            <div className="analysis-row">
              <span>Safety Score</span>
              <span className={`analysis-val ${selectedRoute.safety_score > 0.6 ? "good" : "warn"}`}>
                {Math.round(selectedRoute.safety_score * 100)}%
              </span>
            </div>
            <div className="analysis-row">
              <span>Driver Score</span>
              <span className={`analysis-val ${selectedRoute.driver_score > 0.6 ? "good" : "warn"}`}>
                {Math.round(selectedRoute.driver_score * 100)}%
              </span>
            </div>
            <div className="analysis-row">
              <span>ETA</span>
              <span className="analysis-val neutral">{selectedRoute.eta_minutes} min</span>
            </div>
            <div className="analysis-row">
              <span>Distance</span>
              <span className="analysis-val neutral">{selectedRoute.distance_km} km</span>
            </div>
          </div>
        </div>
      )}

      <div className="insights-section">
        <h3 className="insights-title">Share Your Road Feedback</h3>
        <textarea
          className="feedback-textarea"
          placeholder="Tell us about the road... e.g. 'Potholes near Koyambedu, road is very rough'"
          value={feedbackText}
          onChange={(e) => setFeedbackText(e.target.value)}
          rows={3}
        />
        <button className="analyse-btn" onClick={handleAnalyse} disabled={submitting || !feedbackText.trim()}>
          <Send size={13} />
          {submitting ? "Analysing..." : "Analyse Sentiment"}
        </button>

        {sentimentResult && (
          <div className={`sentiment-result ${sentimentResult.label}`}>
            <strong>
              {sentimentResult.label === "positive" ? "✅" : sentimentResult.label === "negative" ? "⚠️" : "ℹ️"}
              {" "}{sentimentResult.label.charAt(0).toUpperCase() + sentimentResult.label.slice(1)}
            </strong>
            <span> · {Math.round(sentimentResult.score * 100)}% confidence</span>
            {Object.keys(sentimentResult.road_aspects).length > 0 && (
              <ul className="aspects-list">
                {Object.entries(sentimentResult.road_aspects).map(([k, v]) => (
                  <li key={k}><b>{k}:</b> {v}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
