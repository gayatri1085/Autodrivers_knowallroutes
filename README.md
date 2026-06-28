# 🚖 AutoRouteAI

> Navigation inspired by local auto drivers — for roads that Google Maps doesn't truly know.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenStreetMap](https://img.shields.io/badge/Data-OpenStreetMap-orange.svg)](https://openstreetmap.org)

---

## What is AutoRouteAI?

Standard navigation apps optimise for **shortest distance** or **fastest ETA** — metrics that work well on highways but fail on Indian city roads.

A seasoned auto driver in Chennai or Bengaluru uses something different:

- Avoids roads that flood during monsoon
- Knows which narrow lanes have one-way traffic but no signage
- Prefers smooth asphalt over the "technically shorter" pothole stretch
- Skips the main road at school-dismissal time
- Chooses roads with shade in summer

**AutoRouteAI encodes that local knowledge** using AI, driver feedback sentiment, real-time traffic, road quality scoring, and multi-objective graph routing — to produce routes that feel like a local recommended them.

---

## Cities Supported

| City | Status |
|------|--------|
| 🔵 Chennai | Active |
| 🔵 Bengaluru | Active |
| 🔵 Hyderabad | Active |
| 🔵 Kochi | Active |
| 🟡 Coimbatore | In Progress |
| 🟡 Madurai | In Progress |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│   MapLibre GL  │  SearchBar  │  RouteCard  │  Insights  │
└────────────────────────┬────────────────────────────────┘
                         │ REST / WebSocket
┌────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                         │
│  /route  │  /traffic  │  /sentiment  │  /road_score     │
└──────┬───────────┬────────────┬──────────────┬──────────┘
       │           │            │              │
  ┌────▼────┐ ┌───▼────┐ ┌────▼────┐ ┌───────▼──────┐
  │ Routing │ │Traffic │ │Sentiment│ │  Road Quality │
  │ Engine  │ │Predict │ │Analyser │ │  Scorer       │
  │ A* + AI │ │LightGBM│ │RoBERTa  │ │  + Satellite  │
  └────┬────┘ └───┬────┘ └────┬────┘ └───────┬──────┘
       │           │            │              │
  ┌────▼───────────▼────────────▼──────────────▼──────┐
  │              PostGIS + NetworkX Graph              │
  │         OSM Data  │  Driver Feedback  │  Weather   │
  └────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, MapLibre GL JS, Tailwind CSS |
| Backend | Python 3.11, FastAPI, Uvicorn |
| Routing | NetworkX, OSRM, A\*, Dijkstra, Yen's K-Shortest |
| AI/ML | PyTorch, HuggingFace Transformers (RoBERTa), Sentence Transformers |
| Ranking | LightGBM, XGBoost |
| Geo | GeoPandas, Shapely, PostGIS |
| Map Data | OpenStreetMap, Overpass API |
| Database | PostgreSQL + PostGIS |
| Container | Docker, Docker Compose |

---

## Features

- 🗺️ **Multi-objective Routing** — balances time, road quality, safety, and driver preference
- 🧠 **AI Route Re-ranking** — trained on driver sentiment and feedback data
- 🚦 **Traffic Prediction** — time-of-day and event-aware congestion model
- 🛣️ **Road Quality Score** — derived from OSM tags, satellite imagery, and user reports
- 💬 **Driver Sentiment Analysis** — NLP on auto driver community forums and reviews
- 🛰️ **Satellite View** — road surface condition overlaid on satellite tiles
- 🌧️ **Weather-aware Routing** — avoids flood-prone roads during rain
- 🌙 **Dark Mode**
- ♻️ **Alternative Routes** — Yen's K-Shortest Paths with diverse options
- 📊 **Route Insights** — ETA, road score, safety score, driver confidence

---

## Quick Start

### Prerequisites

- Docker + Docker Compose
- Node.js 18+
- Python 3.11+

### 1. Clone

```bash
git clone https://github.com/yourusername/AutoRouteAI.git
cd AutoRouteAI
```

### 2. Configure

```bash
cp backend/config.example.py backend/config.py
# Edit config.py with your API keys (ORS, OpenWeather, etc.)
```

### 3. Download OSM Data

```bash
python scripts/download_osm.py --city chennai
python scripts/build_graph.py --city chennai
```

### 4. Run with Docker

```bash
docker-compose up --build
```

Visit `http://localhost:5173` for the frontend.
API docs at `http://localhost:8000/docs`.

### 5. Run Locally (Dev)

```bash
# Backend
cd backend
pip install -r ../requirements.txt
uvicorn app:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## API Reference

### `POST /route`

```json
{
  "origin": [13.0827, 80.2707],
  "destination": [13.0604, 80.2496],
  "city": "chennai",
  "preferences": {
    "avoid_floods": true,
    "road_quality_weight": 0.4,
    "time_weight": 0.4,
    "driver_score_weight": 0.2
  }
}
```

Response includes ranked routes with `driver_score`, `road_quality`, `safety_score`, `eta_minutes`.

### `GET /traffic?lat=13.08&lng=80.27&city=chennai`

### `GET /road_score?way_id=123456`

### `POST /sentiment` — Analyse driver feedback text

### `POST /feedback` — Submit route feedback to improve the model

See full docs at `/docs` after starting the server.

---

## Data Sources

| Source | Used For |
|--------|---------|
| OpenStreetMap | Road graph, lane info, road type |
| Overpass API | Real-time OSM queries |
| OSRM | Fast baseline routing |
| OpenWeatherMap | Rain / flood risk |
| Google Maps Traffic (scrape) | Traffic ground truth (research) |
| Reddit r/Chennai, r/bangalore | Driver sentiment corpus |
| Auto driver forums | Local route knowledge |
| Bharat Maps / ISRO Bhuvan | Satellite road quality |

---

## Models

| Model | Purpose | Architecture |
|-------|---------|-------------|
| `sentiment_classifier.pkl` | Classify driver feedback as positive/negative/neutral per road | Fine-tuned RoBERTa |
| `route_ranker.pkl` | Re-rank candidate routes by driver score | LightGBM |
| `traffic_model.pkl` | Predict congestion for next 30/60/90 min | XGBoost + temporal features |

### Training

```bash
# Sentiment model
python scripts/train_sentiment.py --data data/sentiment/

# Route ranker
python scripts/train_ranker.py --data data/traffic/

# See notebooks/ for exploration
```

---

## Algorithms

### Route Generation

1. **Build Graph** — OSM road network loaded into NetworkX with edge weights
2. **A\* Search** — Fast initial path with geographic heuristic
3. **Yen's K-Shortest** — Generate K diverse candidate routes
4. **AI Re-ranking** — Score each route with the trained ranker model
5. **Final Output** — Top 3 routes with full metadata

### Road Scoring

Each OSM way gets a composite score:

```
road_score = (
  0.3 × surface_quality +
  0.2 × lane_width +
  0.2 × driver_sentiment +
  0.15 × accident_history_inverse +
  0.15 × flood_risk_inverse
)
```

---

## Project Structure

```
AutoRouteAI/
├── frontend/          # React app with MapLibre
├── backend/           # FastAPI server
│   ├── api/           # Route handlers
│   ├── routing/       # Graph + algorithm logic
│   ├── ai/            # ML models and inference
│   ├── database/      # Schema and ORM models
│   └── utils/         # Geo helpers
├── data/              # Raw and processed data
├── models/            # Trained model artefacts
├── scripts/           # Data pipeline scripts
├── notebooks/         # Exploration and demos
├── docs/              # Architecture diagrams
└── tests/             # Unit and integration tests
```

---

## Contributing

Contributions welcome! Areas most needed:

- Road quality scoring for additional cities
- Driver sentiment corpus expansion (Tamil, Telugu, Malayalam)
- Satellite image road surface classifier
- Mobile app (React Native)

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Roadmap

- [ ] Graph Neural Network for route scoring
- [ ] Real-time driver reporting (crowdsource)
- [ ] Multilingual voice guidance (Tamil, Telugu, Kannada, Malayalam)
- [ ] Two-wheeler optimised routing
- [ ] Integration with BMTC / MTC bus data
- [ ] Offline maps support

---

## License

MIT — see [LICENSE](LICENSE).

---

## Acknowledgements

- OpenStreetMap contributors
- OSRM project
- HuggingFace for transformer models
- The auto drivers of Chennai, Bengaluru, Hyderabad, and Kochi whose knowledge this project tries to encode
