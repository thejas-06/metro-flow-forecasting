# ⚡ FastAPI Production Serving & Inference Layer
### High-Performance REST API Architecture for Real-Time Time-Series Forecasting

This directory contains the production serving layer that exposes the trained **XGBoost Regressor** and autoregressive forecasting chain over a secure, high-throughput **FastAPI REST backend**.

---

## 🏛️ Architecture & Request Lifecycle

```
                                  INFERENCE REQUEST LIFECYCLE
                                  
  Client Request (Browser / External API)
         │
         ▼
  [Security Middleware]   ──►  CORS check, Security Headers (CSP, X-Frame-Options), Rate Limiting
         │
         ▼
  [Pydantic v2 Schema]   ──►  Type verification, bounds validation (Dates 2020–2027, Station sanitization)
         │
         ▼
  [APIRouter Layer]       ──►  Route dispatch (/api/predict/single, /api/predict/forecast, /api/stations)
         │
         ▼
  [MetroPredictor State]  ──►  Feature synthesis (Cyclical hour encoding, station priors, recursive lags)
         │
         ▼
  [XGBoost Model (.pkl)] ──►  Sub-50ms inference execution
         │
         ▼
  [Post-Processing]       ──►  Calculate 95% Confidence Bounds (±1.96·RMSE), classify congestion tiers
         │
         ▼
  JSON Response Payload
```

---

## 📂 Module Breakdown & Code Organization

```text
backend/
├── main.py              # Application entrypoint & async lifespan state manager
├── predictor.py         # XGBoost inference engine & autoregressive forecast chain
├── schemas.py           # Strict Pydantic v2 validation contracts
├── core/
│   └── security.py      # CORS policy, SecurityHeadersMiddleware & SlowAPI rate limiter
└── api/
    ├── router.py        # Top-level API router aggregator
    └── routes/
        ├── predict.py   # Single-hour & 24-hour forecast endpoints
        └── stations.py  # Station metadata and volume tier retrieval
```

### 1. [`main.py`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/backend/main.py) — Application Entry & Lifespan Management
* **Lifespan Context (`@asynccontextmanager`):** Replaces legacy startup events. Loads `MetroPredictor()` into `app.state.predictor` during boot, ensuring model weights are warm in memory and startup errors cleanly surface in logs without crashing at module import time.
* **Static Asset Serving:** Mounts the frontend SPA and serves `index.html` at the root path (`/`).
* **OpenAPI Documentation:** Auto-generates interactive Swagger UI (`/docs`) and ReDoc (`/redoc`).

### 2. [`predictor.py`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/backend/predictor.py) — Inference Engine & Autoregressive Forecaster
* **Single Prediction (`predict_single`):**
  * Dynamically computes the 19 required features (cyclical hour $\sin/\cos$, calendar flags, station volume priors).
  * Computes 95% confidence intervals: $[\hat{y} - 1.96 \cdot \text{RMSE}, \hat{y} + 1.96 \cdot \text{RMSE}]$.
  * Classifies passenger load into 4 operational congestion tiers: `NORMAL / CLEAR`, `MODERATE`, `HEAVY`, `CRITICAL SURGE`.
* **24-Hour Forecast (`predict_24h_forecast`):**
  * Executes a closed-loop autoregressive forecasting loop (`for h in range(24)`).
  * Automatically rolls forward previous hour predictions as inputs (`Lag_1h`, `Lag_2h`, `Rolling_3h`) for subsequent hours.

### 3. [`schemas.py`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/backend/schemas.py) — Strict Pydantic Data Contracts
* **Input Validation:** Enforces strict ISO dates (`DateType` constrained between `2020-01-01` and `2027-12-31`), integer hours (`0 <= hour <= 23`), and non-empty station strings.
* **Contract Protection:** Strips internal model debugging artifacts (e.g. `features_used`) from external JSON responses to ensure clean API versioning.

### 4. [`core/security.py`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/backend/core/security.py) — Security & Rate Limiting
* **SecurityHeadersMiddleware:** Adds `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and strict Content Security Policy (`CSP`). Sets `Strict-Transport-Security` conditionally on HTTPS connections.
* **CORS Configuration:** Explicit origin whitelisting with credentials spec compliance.
* **SlowAPI Rate Limiting:** Protects endpoints against abuse (30 req/min on single prediction, 15 req/min on 24h forecasts).

---

## 🔌 API Endpoints Reference

### `GET /health`
* **Purpose:** Health check & readiness verification.
* **Response Model:** `HealthResponse`
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "model_loaded": true,
  "total_stations": 83,
  "data_file_present": true
}
```

### `GET /api/stations`
* **Purpose:** Returns the complete list of 83 stations with volume tiers and daily average estimates.
* **Rate Limit:** 60 requests / minute

### `POST /api/predict/single`
* **Purpose:** Predicts passenger flow for a specific station, date, and hour.
* **Rate Limit:** 30 requests / minute
* **Request:**
```json
{
  "station": "Nadaprabhu Kempegowda Station, Majestic",
  "date": "2025-09-25",
  "hour": 9
}
```
* **Response:**
```json
{
  "station": "Nadaprabhu Kempegowda Station, Majestic",
  "date": "2025-09-25",
  "hour": 9,
  "predicted_boarding": 2377,
  "congestion_level": "CRITICAL SURGE",
  "is_peak_hour": true,
  "confidence_interval": {
    "lower_bound": 2215.5,
    "upper_bound": 2538.5,
    "confidence_level": "95%"
  }
}
```

### `POST /api/predict/forecast`
* **Purpose:** Returns a 24-hour continuous autoregressive timeline curve.
* **Rate Limit:** 15 requests / minute
* **Request:**
```json
{
  "station": "Indiranagar",
  "date": "2025-09-25"
}
```

---

## 🚀 Running & Validating the Backend

### 1. Start the API Server
```powershell
# Windows
.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Run Automated API Tests
```powershell
.venv\Scripts\python -m pytest tests/test_api.py -v
```

* **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Interface:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
