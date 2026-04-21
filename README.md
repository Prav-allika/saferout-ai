---
title: SafeRoute AI
emoji: S
colorFrom: blue
colorTo: pink
sdk: streamlit
sdk_version: 1.28.0
app_file: ui/dashboard.py
pinned: false
---

**Live Demo:** https://huggingface.co/spaces/Prav04/saferout-ai

# SafeRoute AI — Multi-Agent Vehicle Safety Monitoring System

An intelligent multi-agent AI system that predicts vehicle failures, analyzes route safety, and executes automated emergency protocols using machine learning and real-time sensor simulation.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![ML](https://img.shields.io/badge/ML-Random%20Forest-green.svg)](https://scikit-learn.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

---

## Project Overview

SafeRoute AI is a vehicle safety monitoring system built with Python, scikit-learn, and a multi-agent architecture. It processes simulated IoT sensor data — tire pressure, engine temperature, road conditions, weather — to predict failures before they happen and automatically trigger emergency protocols.

The system is designed as a portfolio demonstration of multi-agent coordination, real-time ML inference, and scalable Python architecture.

---

## System Architecture

```
+-----------------------------------------------------+
|                    ORCHESTRATOR                      |
|                 (Master Controller)                  |
|   - Runs route + tire + engine checks in parallel   |
|   - Calculates risk level: LOW / MEDIUM / HIGH      |
|   - Routes decisions to specialized agents          |
+-------------+---------------+---------------+-------+
              |               |               |
              v               v               v
       +-----------+   +-----------+   +-----------+
       |   TIRE    |   | EMERGENCY |   |   ROUTE   |
       | PREDICTOR |   | RESPONDER |   | ANALYZER  |
       |           |   |           |   |           |
       | Random    |   | Protocols |   | Weather + |
       | Forest ML |   | SMS/Calls |   | Road Risk |
       | Inference |   | Automated |   | Scoring   |
       +-----------+   +-----------+   +-----------+
```

---

## Agents

### 1. Tire Predictor Agent

- Random Forest classifier trained on 10,000 synthetic samples
- Predicts tire failure probability up to 48 hours ahead
- Features: pressure (PSI), temperature, age, rotation history, mileage
- Training data generated with vectorized NumPy operations (~100x faster than a Python loop)
- Model persisted to disk (`models/tire_model.pkl`) — auto-loaded on startup, no retraining needed
- Real-time probability scoring with HIGH / MEDIUM confidence levels

### 2. Emergency Responder Agent

- Classifies incoming critical alerts and executes the matching protocol
- **Tire Critical:** SMS driver → call garage → notify manager → log event → disable vehicle start
- **Engine Critical:** Stop instructions → dispatch tow → notify passengers → log event
- **Multiple Failures:** Escalated multi-system response
- Priority system: IMMEDIATE > CRITICAL > HIGH > MEDIUM
- Bounded history buffer (deque, maxlen=500) — prevents unbounded memory growth

### 3. Route Analyzer Agent

- Combines weather simulation with a road accident database
- Risk formula: `base_risk * weather_multiplier * time_multiplier`
- Evidence-based multipliers (rain = 1.8x, night = 1.3x — sourced from NHTSA research)
- Suggests alternative routes with quantified risk reduction
- Results cached for 30 ticks (~30 seconds) to avoid redundant recomputation
- Bounded history buffer (deque, maxlen=500)

### 4. Orchestrator (Master Controller)

- Runs route analysis, tire checks, and engine checks in parallel using `ThreadPoolExecutor`
- Merges results and determines overall risk level
- Routes HIGH risk to Emergency Responder, MEDIUM risk to ML Tire Predictor
- Route analysis cache with configurable TTL (default: 30 ticks)
- Bounded alert history (deque, maxlen=1000)

---

## Project Structure

```
saferout-ai/
├── agents/
│   ├── orchestrator.py          # Master controller — parallel execution, risk routing
│   ├── tire_predictor.py        # ML inference wrapper
│   ├── emergency_responder.py   # Emergency protocol execution
│   └── route_analyzer.py        # Route safety scoring
│
├── models/
│   └── tire_failure_model.py    # Random Forest classifier with auto-save/load
│
├── simulation/
│   ├── sensors.py               # IoT sensor simulation (tire + engine)
│   └── environment.py           # Weather simulator + road accident database
│
├── config/
│   └── settings.py              # Centralized configuration
│
├── ui/
│   └── dashboard.py             # Streamlit real-time dashboard
│
└── requirements.txt
```

---

## Technologies

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Machine Learning | scikit-learn (RandomForestClassifier), NumPy |
| Dashboard | Streamlit, Plotly |
| Concurrency | concurrent.futures.ThreadPoolExecutor |
| Data Structures | collections.deque (bounded buffers) |
| Model Persistence | pickle |

---

## Quick Start

### 1. Create and activate virtual environment

```bash
python3 -m venv saferout
source saferout/bin/activate      # macOS / Linux
saferout\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the dashboard

```bash
streamlit run ui/dashboard.py
```

Dashboard opens at `http://localhost:8501`

---

## Simulation Modes

| Mode | What it simulates |
|---|---|
| `normal` | Baseline driving — sensor values fluctuate within safe ranges |
| `tire_failure` | Front-left tire loses 0.3 PSI per second — triggers WARNING then CRITICAL |
| `engine_overheat` | Engine temperature rises 0.5–2.0 degrees per second — triggers overheat alert |

---

## Performance Optimizations

| Area | Implementation | Benefit |
|---|---|---|
| Parallel agent execution | `ThreadPoolExecutor` (3 workers) | Route + tire + engine checks run concurrently |
| Route analysis caching | 30-tick TTL cache keyed by road + time-of-day | Avoids redundant weather/road API calls |
| Bounded history buffers | `deque(maxlen=N)` on all agents | O(1) append, constant memory regardless of runtime |
| Vectorized ML training | NumPy array operations replacing Python for-loop | ~100x faster data generation at 10,000 samples |
| Model persistence | Auto-save after training, auto-load on startup | Eliminates retraining overhead on every restart |

---

## Risk Level Logic

```
Tire pressure < 28 PSI   ->  TIRE_CRITICAL  (severity: CRITICAL)  ->  risk = HIGH
Tire pressure < 30 PSI   ->  TIRE_WARNING   (severity: WARNING)   ->  risk = MEDIUM
Engine temp > 110 C      ->  ENGINE_CRITICAL (severity: CRITICAL) ->  risk = HIGH
Engine temp > 100 C      ->  ENGINE_WARNING  (severity: WARNING)  ->  risk = MEDIUM
Route risk score >= 6/10 ->  ROUTE_HIGH_RISK (severity: WARNING)  ->  risk = MEDIUM
No alerts                ->  risk = LOW
```

---

## Performance Metrics

| Metric | Value |
|---|---|
| ML model accuracy | 99.8% (training set, 10,000 samples) |
| Training data generation | Vectorized NumPy — ~100x faster than loop |
| Analysis frequency | Every 1 second (dashboard refresh) |
| Orchestrator response | < 500 ms |
| Agents coordinated | 3 specialized agents |
| Sensors monitored | 4 tires + engine (10+ data points per tick) |

---

## Design Decisions

### Why simulation instead of real hardware?

- Works fully offline — no API keys or hardware required during demos
- Instant access to edge cases (critical pressure drop, engine overheat) without waiting
- Algorithm is data-source agnostic — swapping in OpenWeatherMap API or OBD-II adapters requires only changing the data layer

### Why Random Forest?

- Well-suited to tabular sensor data with non-linear relationships
- Returns probability scores, not just binary predictions — enables confidence thresholds
- Fast inference (< 50 ms) suitable for real-time use
- Feature importance is interpretable for debugging and reporting

### Why multi-agent architecture?

- Each agent has a single responsibility — easier to test and modify independently
- New agents (e.g., fuel, battery, GPS) can be added without changing existing ones
- Orchestrator decouples routing logic from execution logic

---

## Future Enhancements

- [ ] Real hardware integration (OBD-II adapters, TPMS sensors)
- [ ] Cloud deployment (AWS Lambda + API Gateway)
- [ ] Real-time GPS tracking and geofencing
- [ ] Historical trend analysis and maintenance scheduling
- [ ] Fleet management view (multiple vehicles)
- [ ] SMS / email notifications via Twilio / SendGrid
- [ ] Database backend (PostgreSQL) for persistent alert history
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)

---

## Author

**Pravalli**  
ML Engineer — Hyderabad, India  
GitHub: [Prav-allika](https://github.com/Prav-allika)

---

## License

MIT License — open source, free to use and modify.

---

## Acknowledgments

- Risk multipliers based on NHTSA and WHO road safety research
- ML training methodology from scikit-learn documentation
- Dashboard built with Streamlit and Plotly
