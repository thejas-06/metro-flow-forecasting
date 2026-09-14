# 🚇 Namma Metro Passenger Flow Forecasting System
### Production-Grade Machine Learning & REST API Architecture

[![GitHub Repository](https://img.shields.io/badge/GitHub-metro--flow--forecasting-181717?style=flat&logo=github)](https://github.com/thejas-06/metro-flow-forecasting)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-eb5424.svg?style=flat)](https://xgboost.ai)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-e92063.svg?style=flat&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Pytest](https://img.shields.io/badge/Tests-11%20Passed-22c55e.svg?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org)

An end-to-end Machine Learning Engineering system that forecasts hourly commuter passenger flow across all **83 Namma Metro stations** in Bengaluru, Karnataka. Built with a decoupled microservice architecture serving an optimized **XGBoost Regressor** via a high-performance **FastAPI REST backend** to a custom **Vanilla JavaScript dashboard**.

---

## ⚡ System Highlights & Engineering Innovations

* **High-Precision Time-Series Forecasting:** Achieves an **$R^2$ Score of 0.9955 (99.55% variance explained)** with a system-wide weighted MAPE of just **4.08%**.
* **Zero Training-Serving Skew:** Encapsulates the entire feature engineering lifecycle (cyclical trigonometric time transforms, station volume baselines, multi-scale lags) into custom Scikit-Learn `BaseEstimator` and `TransformerMixin` classes.
* **Autoregressive Multi-Step Horizon:** Generates full 24-hour continuous timeline curves via recursive closed-loop lag feedback without requiring live hardware tap-gate dependencies.
* **Production REST API:** Asynchronous FastAPI backend with modern `@asynccontextmanager` lifespan model caching, strict Pydantic v2 validation contracts, SlowAPI rate limiting, and security headers.
* **Zero-Framework Responsive UI:** Lightweight Vanilla HTML5 / CSS3 / ES6 dashboard delivering sub-10ms render times and interactive Chart.js visualizations.

---

## 📂 Monorepo Architecture & Sub-Documentation

This repository is structured as a modular enterprise monorepo. Each component contains dedicated documentation:

```text
metro-flow-forecasting/
├── 🔬 notebooks/           # Research, EDA, Modeling & MLOps Pipelines (01–06)
│   ├── 01_Data_Loading_and_Understanding.ipynb
│   ├── 02_EDA.ipynb
│   ├── 03_Preprocessing_and_Feature_Engineering.ipynb
│   ├── 04_Model_Building.ipynb
│   ├── 05_Deep_Learning_LSTM.ipynb
│   ├── 06_Production_Pipeline_Building.ipynb
│   └── README.md          # 📖 Detailed ML Research & Pipeline Documentation
│
├── ⚡ backend/             # Production FastAPI Model Serving Layer
│   ├── api/               # Modular APIRouter endpoints (/predict, /stations)
│   ├── core/              # SecurityHeadersMiddleware, CORS & SlowAPI rate limiting
│   ├── main.py            # Application lifespan entrypoint
│   ├── predictor.py       # Inference engine & autoregressive forecast chain
│   ├── schemas.py         # Strict Pydantic v2 validation contracts
│   └── README.md          # 📖 Detailed API Architecture & Endpoint Reference
│
├── 🎨 frontend/            # Responsive Single-Page Web Dashboard
│   ├── index.html         # Semantic accessible SPA structure
│   ├── css/               # Modular CSS3 design system (base, layout, components)
│   ├── js/                # Modular ES6 client (main, api, ui, charts)
│   └── README.md          # 📖 Detailed UI/UX & Design System Documentation
│
├── 🧪 tests/               # Automated Test Suite (11/11 Passed)
│   └── test_api.py        # Edge-case validation, health & inference integration tests
│
├── 💾 data/                # Raw RTI records & processed feature tables
├── 📦 models/              # Serialized pipeline artifacts (.joblib, .pkl & metadata)
├── requirements.txt       # Production dependencies
└── .gitignore             # Environment & cache isolation rules
```

* 🔬 **[Read the Machine Learning Research Documentation (notebooks/README.md)](notebooks/README.md)**
* ⚡ **[Read the FastAPI Backend Architecture Documentation (backend/README.md)](backend/README.md)**
* 🎨 **[Read the Frontend Dashboard Documentation (frontend/README.md)](frontend/README.md)**

---

## 📊 Model Performance & Benchmarking

| Model Architecture | Category | RMSE | MAE | $R^2$ Score | System WMAPE | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Ridge Regression** | Regularized Linear | `142.42` | `74.11` | `0.9107` | `19.32%` | Baseline |
| **Dense MLP** | Feed-Forward Neural Net | `130.54` | `81.46` | `0.9258` | `21.40%` | Baseline sequence |
| **Stacked Bi-LSTM** | Recurrent Neural Net | `113.46` | `60.57` | `0.9440` | `14.94%` | Sequence baseline |
| **Random Forest** | Bagging Ensemble | `83.70` | `41.81` | `0.9692` | `9.23%` | Non-linear baseline |
| **Tuned XGBoost** | Gradient Boosted Trees | `82.40` | `43.85` | `0.9701` | `8.77%` | Selected Model |
| **End-to-End Pipeline** | Unified Scikit-Learn + XGBoost | **`32.01`** | **`14.56`** | **`0.9955`** | **`4.08%`** | **🏆 Production Artifact** |

---

## 🚀 Quickstart: Running Locally

### 1. Clone the Repository
```bash
git clone https://github.com/thejas-06/metro-flow-forecasting.git
cd metro-flow-forecasting
```

### 2. Set Up Virtual Environment
```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Automated Test Suite
```bash
pytest tests/test_api.py -v
```

### 5. Launch the Application
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

* 🌐 **Web Dashboard:** [http://localhost:8000](http://localhost:8000)
* ⚡ **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* 📖 **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description | Rate Limit |
| :--- | :--- | :--- | :---: |
| `GET` | `/health` | Server readiness, version, and model status | Unlimited |
| `GET` | `/api/stations` | All 83 metro stations with traffic volume tiers | 60 / min |
| `POST` | `/api/predict/single` | Single-hour flow forecast with 95% confidence intervals | 30 / min |
| `POST` | `/api/predict/forecast` | Full 24-hour continuous autoregressive timeline curve | 15 / min |

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
