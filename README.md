#  SafeRoute AI - Multi-Agent Vehicle Safety Monitoring System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![ML](https://img.shields.io/badge/ML-Random%20Forest-green.svg)](https://scikit-learn.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

An intelligent multi-agent AI system that predicts vehicle failures, analyzes route safety, and executes automated emergency protocols using machine learning and real-time sensor simulation.

##  Project Overview

SafeRoute AI is a production-grade vehicle safety monitoring system built with **Python, Machine Learning, and Multi-Agent Architecture**. The system analyzes real-time sensor data (tire pressure, engine temperature, road conditions, weather) to predict failures **before they happen** and automatically execute emergency protocols.

###  Key Highlights

- ** 3 Specialized AI Agents** coordinated by a master orchestrator
- ** ML-Powered Predictions** using Random Forest (99.8% accuracy)
- ** Real-Time Analysis** processing sensor data every 5 seconds
- ** Automated Emergency Response** with multi-step protocols
- ** Dynamic Route Risk Analysis** combining weather + road conditions
- ** Interactive Dashboard** built with Streamlit

---

##  System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  ORCHESTRATOR                        │
│              (Master Controller)                     │
│   • Analyzes sensors every 5 seconds                │
│   • Calculates risk: LOW/MEDIUM/HIGH                │
│   • Routes decisions to specialized agents          │
└──────────┬──────────────┬──────────────┬───────────┘
           │              │              │
           ↓              ↓              ↓
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │   TIRE   │   │ EMERGENCY│   │  ROUTE   │
    │PREDICTOR │   │RESPONDER │   │ ANALYZER │
    │          │   │          │   │          │
    │ ML Model │   │ Protocols│   │ Weather+ │
    │ Predicts │   │ SMS/Calls│   │ Road Risk│
    │ Failures │   │ Automated│   │ Analysis │
    └──────────┘   └──────────┘   └──────────┘
```

---

##  Features

### 1️ **Tire Failure Predictor Agent**
- Random Forest ML model trained on 10,000 synthetic examples
- Predicts tire failures up to 48 hours in advance
- 99.8% training accuracy
- Features: pressure, temperature, age, rotation history, mileage
- Real-time probability scoring with confidence levels

### 2️ **Emergency Responder Agent**
- Automated emergency protocols based on severity
- **Tire Critical Protocol:** SMS driver → Call garage → Notify manager → Log event → Disable vehicle start (5 automated actions)
- **Engine Critical Protocol:** Emergency stop instructions → Dispatch tow truck → Notify passengers
- **Multi-Failure Protocol:** Escalated response for cascading failures
- Priority system: IMMEDIATE > CRITICAL > HIGH > MEDIUM

### 3️ **Route Analyzer Agent**
- Combines weather simulation + road accident database
- Dynamic risk calculation: `base_risk × weather_multiplier × time_multiplier`
- Evidence-based multipliers (NHTSA research: rain = 1.8×, night = 1.3×)
- Suggests alternative routes with risk reduction estimates
- Tracks accident history (6-month rolling data)

### 4️ **Orchestrator (Master AI)**
- Coordinates all 3 specialized agents
- Multi-source analysis (tires + engine + route)
- Risk-based intelligent routing
- Complete audit trail with timestamps
- Statistics tracking for monitoring

---

##  Project Structure

```
saferout-ai/
├── agents/                      #  Specialized AI Agents
│   ├── orchestrator.py          # Master controller (280 lines)
│   ├── tire_predictor.py        # ML predictions (78 lines)
│   ├── emergency_responder.py   # Emergency protocols (229 lines)
│   └── route_analyzer.py        # Route safety (144 lines)
│
├── models/                      #  Machine Learning
│   └── tire_failure_model.py    # Random Forest classifier (192 lines)
│
├── simulation/                  # Data Simulation
│   ├── sensors.py               # IoT sensor simulation (158 lines)
│   └── environment.py           # Weather + road database (263 lines)
│
├── config/                      #  Configuration
│   └── settings.py              # Central settings (45 lines)
│
├── utils/                       #  Utilities
│   ├── logger.py                # Production logging (158 lines)
│   ├── data_processor.py        # Data validation
│   └── monitoring.py            # Performance tracking
│
├── ui/                          # User Interface
│   └── dashboard.py             # Streamlit dashboard
│
├── main.py                      # Entry point
├── requirements.txt             #  Dependencies
└── README.md                    #  Documentation
```

**Total:** ~2,000 lines of production-quality Python code

---

##  Technologies Used

### **Core Technologies**
- **Python 3.8+** - Primary language
- **Machine Learning:** scikit-learn (Random Forest), NumPy
- **Web Framework:** Streamlit (interactive dashboard)
- **Data Processing:** Pydantic (validation), Pandas

### **AI/ML Stack**
- Random Forest Classifier
- Feature engineering (5 features)
- Synthetic training data generation
- Probability scoring with confidence levels

### **Architecture Patterns**
- Multi-agent system design
- Event-driven architecture
- Singleton pattern (logger, settings)
- Strategy pattern (emergency protocols)

---

##  Quick Start

### **1. Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/saferout-ai.git
cd saferout-ai
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Test Installation**
```bash
python quick_test.py
```

Expected output:
```
 Testing SafeRoute AI System...
 All imports successful!
 Orchestrator created successfully!
 Vehicle created! ID: TEST-123
 Analysis complete!
 ML model works!
 ALL TESTS PASSED!
```

### **4. Run Dashboard**
```bash
streamlit run ui/dashboard.py
```

Dashboard opens at `http://localhost:8501`

---

##  Demo & Screenshots

### **Real-Time Monitoring**
- Live sensor data from 4 tire sensors + engine
- Pressure, temperature, age, rotation tracking
- Color-coded status indicators

### **ML Predictions**
- Failure probability with time estimates
- Confidence scoring (HIGH/MEDIUM)
- Actionable recommendations

### **Emergency Alerts**
- Automated SMS notifications (simulated)
- Multi-step protocol execution
- Complete audit trail

### **Route Analysis**
- Weather-aware risk calculation
- Alternative route suggestions
- Historical accident data integration

---

##  Testing

Run comprehensive tests:
```bash
python quick_test.py
```

Tests cover:
-  Import validation
-  Orchestrator initialization
-  Vehicle simulation
-  Sensor data analysis
-  ML model predictions
-  Agent coordination

---

##  Performance Metrics

| Metric | Value |
|--------|-------|
| **ML Model Accuracy** | 99.8% (training) |
| **Sensor Processing** | 150 μs per reading |
| **Analysis Frequency** | Every 5 seconds |
| **Response Time** | <500ms (orchestrator) |
| **Agents Coordinated** | 3 specialized agents |
| **Data Points** | 10+ sensors per vehicle |

---

##  Technical Highlights (Resume-Ready)

### **Machine Learning**
- Designed and trained Random Forest classifier with 100 estimators
- Achieved 99.8% accuracy on 10,000 synthetic training samples
- Implemented custom feature engineering pipeline (5 features)
- Real-time inference with <50ms latency

### **System Architecture**
- Built multi-agent AI system with centralized orchestration
- Implemented risk-based routing algorithm (LOW/MEDIUM/HIGH)
- Designed 3 specialized agents with single responsibility principle
- Created event-driven architecture with complete audit trails

### **Data Engineering**
- Simulated realistic IoT sensor data with gradual failure modes
- Integrated multiple data sources (sensors, weather, road database)
- Implemented data validation with Pydantic models
- Built production-grade logging system with 3 output streams

### **Software Engineering**
- Wrote 2,000+ lines of production-quality Python
- Followed clean code principles (DRY, SOLID)
- Comprehensive error handling and edge case coverage
- Modular design for easy testing and maintenance

---

##  Future Enhancements

### **Planned Features**
- [ ] Real hardware integration (OBD-II adapters, TPMS)
- [ ] Cloud deployment (AWS Lambda, API Gateway)
- [ ] Mobile app (Flutter)
- [ ] Real-time GPS tracking
- [ ] Historical trend analysis
- [ ] Fleet management dashboard
- [ ] SMS/email notifications (Twilio, SendGrid)
- [ ] Database integration (PostgreSQL)
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)

---

##  Project Decisions & Rationale

### **Why Simulation Instead of Real Hardware?**
- **Demo Reliability:** Works offline, no API failures during interviews
- **Cost:** $0 vs $600+/month for real-time APIs
- **Testing:** Instant access to edge cases (storm, fog, night)
- **Focus:** Demonstrates AI decision logic, not data engineering

**Production Approach:** Would integrate OpenWeatherMap API, data.gov.in (accident data), OBD-II adapters. Algorithm is data-source agnostic.

### **Why Random Forest?**
- Excellent for tabular data (sensor readings)
- Handles non-linear relationships
- Provides probability scores (not just binary)
- Fast inference (<50ms)
- Interpretable (feature importance)

### **Why Multi-Agent Architecture?**
- **Separation of Concerns:** Each agent has single responsibility
- **Scalability:** Easy to add more agents (weather, traffic, maintenance)
- **Testability:** Agents can be tested independently
- **Maintainability:** Changes to one agent don't affect others

---

##  Author

**Pravalli** - ML Engineer  
-  Email: pravallipasala@gmail.com
-  LinkedIn: https://github.com/Prav-allika
-  Portfolio: [Your Portfolio]
-  Location: Hyderabad, India

---

##  License

This project is open source and available under the MIT License.

---

##  Acknowledgments

- **ML Model Training:** scikit-learn community
- **Risk Multipliers:** NHTSA and WHO road safety research
- **Dashboard Framework:** Streamlit team
- **Architecture Inspiration:** Multi-agent systems literature

---

##  Contact & Collaboration

Interested in this project? Have questions? Want to collaborate?

- Open an issue on GitHub
- Connect on LinkedIn
- Check out my other projects: [GitHub Profile]

---

** If you found this project helpful, please give it a star!**

** Keywords:** Python, Machine Learning, AI, Multi-Agent Systems, IoT, Random Forest, Streamlit, Real-Time Processing, Safety Monitoring, Predictive Maintenance
