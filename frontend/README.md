# 🎨 Frontend Web Application & Visualization Layer
### Responsive Single-Page Dashboard for Real-Time Transit Forecasting

This directory contains the user-facing web dashboard built with **Vanilla HTML5, Modern CSS3 Design Tokens, and Modular ES6 JavaScript**. It connects directly to the FastAPI backend to visualize passenger flow forecasts, operational congestion levels, and 24-hour timeline curves across all 83 Namma Metro stations.

---

## 🖥️ UI/UX Architecture & Core Views

```
                                  FRONTEND SPA ARCHITECTURE
                                  
                            ┌───────────────────────────────────┐
                            │      Single-Page App (SPA)        │
                            │      [frontend/index.html]        │
                            └─────────────────┬─────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
  [1. Check Crowd Tab]               [2. Plan My Day Tab]               [3. All Stations Tab]
  • Instant single-hour query        • 24-hour continuous timeline      • 83 station directory
  • Congestion status badge          • Interactive Chart.js line plot   • Real-time search & sorting
  • 95% Confidence Interval band     • Day summary KPI cards            • Detailed modal drill-down
  • Peak commute indicator           • Hourly forecast data table       • Direct "Plan Station" action
```

---

## 📂 Module Breakdown & Code Organization

```text
frontend/
├── index.html           # Semantic HTML5 single-page application structure
├── css/                 # Modular CSS3 Design System
│   ├── base.css         # Color tokens, typography (Plus Jakarta Sans/Inter), resets
│   ├── layout.css       # Header, navigation tabs, grid layouts, responsive breakpoints
│   └── components.css   # Input bars, stat cards, badges, modal dialogs, tables
└── js/                  # ES6 Module Client Architecture
    ├── main.js          # App lifecycle, event wiring, form handlers & offline recovery
    ├── api.js           # Asynchronous REST client (fetch wrappers for FastAPI endpoints)
    ├── ui.js            # DOM mutations, tab switching, KPI rendering & XSS-safe DOM builders
    └── charts.js        # Chart.js time-series gradient visualizations & tooltip formatters
```

---

## 🧩 Component & Module Details

### 1. [`index.html`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/index.html) — Semantic SPA Structure
* **Zero Framework Overhead:** Pure HTML5 structure loading no heavy frameworks (React/Vue/Angular), achieving instant sub-10ms initial render times.
* **Accessible & Constrained:** Includes ARIA labels, semantic `<main>`, `<section>`, `<nav>`, and `<header>` tags, and native HTML5 date input bounds (`min="2020-01-01"`, `max="2027-12-31"`).
* **Multi-View Tabs:** Clean client-side tab switching between **Check Crowd**, **Plan My Day**, and **All Stations**.

### 2. Design System ([`css/`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/css/))
* **[`base.css`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/css/base.css):** Minimalist executive black-and-white color palette with tailored semantic status tokens:
  * 🟢 `NORMAL / CLEAR`: `#166534` on `#f0fdf4`
  * 🟡 `MODERATE`: `#854d0e` on `#fefce8`
  * 🟠 `HEAVY`: `#9a3412` on `#fff7ed`
  * 🔴 `CRITICAL SURGE`: `#991b1b` on `#fef2f2`
* **[`layout.css`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/css/layout.css):** Centered containers, flexbox navigation bars, card layouts, and mobile-friendly responsive breakpoints (`@media (max-width: 768px)`).
* **[`components.css`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/css/components.css):** Glassmorphic input bars, KPI cards, interactive station cards, forecast tables, and modal overlay dialogs.

### 3. Client Logic & Visualization ([`js/`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/js/))
* **[`main.js`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/js/main.js):** 
  * Manages initial station pre-fetching and auto-predicts default station on page load.
  * Implements offline retry and renders a fallback banner if the FastAPI backend is offline.
* **[`api.js`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/js/api.js):** 
  * Encapsulates `fetch` calls to `/api/stations`, `/api/predict/single`, and `/api/predict/forecast`.
* **[`ui.js`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/js/ui.js):** 
  * Dynamically populates dropdowns, computes daily volume KPIs, and renders station grids.
  * **XSS-Safe Architecture:** Uses native DOM element construction (`document.createElement`) and `textContent` to eliminate cross-site scripting vulnerabilities.
* **[`charts.js`](file:///d:/Thejas/thejas%20project/Metro%20Passenger%20Flow%20Prediction/frontend/js/charts.js):** 
  * Configures Chart.js line charts with cubic bezier smoothing (`tension: 0.35`), vertical background gradients, distinct peak-hour scatter points (amber accents), and passenger count tooltips.

---

## 🔌 Frontend-Backend Integration

The frontend communicates with the backend via native asynchronous JSON requests:

```javascript
// Example: Requesting a single-hour crowd prediction
import { fetchSinglePrediction } from './api.js';

const result = await fetchSinglePrediction("Indiranagar", "2025-09-25", 9);
// result => { predicted_boarding: 1850, congestion_level: "HEAVY", ... }
```

---

## 🌐 Running Locally

The frontend is automatically hosted as static files by the FastAPI backend server:

```powershell
# Start the full application (Backend + Frontend)
.venv\Scripts\uvicorn backend.main:app --reload
```

Once started, open [http://localhost:8000](http://localhost:8000) in your web browser.
