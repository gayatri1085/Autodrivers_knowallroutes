# Contributing to AutoRouteAI

Thank you for your interest in improving AutoRouteAI. This document explains how to contribute effectively.

---

## Areas Most Needed

- **Road quality data** for additional South Indian cities
- **Driver sentiment corpus** — Tamil, Telugu, Malayalam, Kannada text
- **Satellite image classifier** — road surface detection from imagery
- **Accident dataset integration** — linking historical data to road segments
- **Mobile app** — React Native wrapper

---

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Set up dev environment: `pip install -r requirements.txt && cd frontend && npm install`
4. Run tests: `pytest tests/`
5. Submit a pull request

---

## Code Style

- Python: Black formatting (`black backend/`), Ruff linting (`ruff check backend/`)
- JavaScript/React: ESLint (`npm run lint`)
- Type hints required for all Python functions
- Docstrings on all public functions and classes

---

## Adding a New City

1. Add bounds to `backend/config.example.py` under `CITY_BOUNDS`
2. Run `python scripts/download_osm.py --city yourcity`
3. Run `python scripts/build_graph.py --city yourcity`
4. Add to `SUPPORTED_CITIES` in `scripts/build_graph.py`
5. Add driver insights to `frontend/src/components/DriverInsights.jsx`
6. Open a PR with the city name in the title

---

## Adding Sentiment Data

Create JSONL files in `data/sentiment/` with one JSON object per line:

```json
{"text": "Road near Koyambedu has too many potholes", "label": "negative"}
{"text": "Smooth ride on Anna Salai this morning", "label": "positive"}
```

Labels: `positive`, `negative`, `neutral`.

Tamil, Telugu, Kannada, and Malayalam samples are especially valuable.

---

## Reporting Issues

Please include:
- City and route (approximate origin/destination)
- Expected vs actual behaviour
- Steps to reproduce
- OS and browser/environment

---

## Code of Conduct

Be respectful. Focus on the work. Disagreements about technical direction should be handled constructively in GitHub issues.
