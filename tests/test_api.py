"""
Pytest Suite — Namma Metro Passenger Flow Prediction API
Validates: health check, stations, single prediction, 24h forecast, edge cases.
"""

import pytest
import os
import sys
from datetime import date

# Ensure the backend directory is resolvable by the test runner
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from main import app

TODAY = date.today().isoformat()


@pytest.fixture(scope="session")
def client():
    """
    Shared TestClient that triggers FastAPI lifespan (model load) once per session.
    Using the context manager ensures app.state.predictor is populated before any test runs.
    """
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health_check(client):
    """Health endpoint should return healthy status with model loaded and station count."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["total_stations"] >= 80
    assert "version" in data
    assert "data_file_present" in data


# ---------------------------------------------------------------------------
# Stations
# ---------------------------------------------------------------------------

def test_get_stations_structure(client):
    """Station list should return all stations with required metadata fields."""
    response = client.get("/api/stations")
    assert response.status_code == 200
    data = response.json()
    assert "total_stations" in data
    assert data["total_stations"] >= 80
    assert len(data["stations"]) >= 80

    station = data["stations"][0]
    assert "name" in station
    assert "avg_hourly_traffic" in station
    assert "traffic_tier" in station
    assert "estimated_daily_traffic" in station


# ---------------------------------------------------------------------------
# Single prediction — happy paths
# ---------------------------------------------------------------------------

def test_single_prediction_peak_hour(client):
    """Peak hour at Majestic should return high boarding count and peak flag."""
    payload = {
        "station": "Nadaprabhu Kempegowda Station, Majestic",
        "date": TODAY,
        "hour": 9,
        "lag_1h": 2200.0,
        "lag_2h": 1800.0,
        "lag_24h": 2100.0
    }
    response = client.post("/api/predict/single", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["hour"] == 9
    assert data["predicted_boarding"] > 500
    assert data["is_peak_hour"] is True
    assert "confidence_interval" in data
    assert "congestion_level" in data
    # features_used must NOT be in the public response
    assert "features_used" not in data


def test_single_prediction_late_night(client):
    """Late night hours (1–3 AM) should return near-zero passenger counts."""
    payload = {
        "station": "Mahatma Gandhi Road",
        "date": TODAY,
        "hour": 2,
        "lag_1h": 0.0,
        "lag_2h": 0.0,
        "lag_24h": 0.0
    }
    response = client.post("/api/predict/single", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["hour"] == 2
    assert data["predicted_boarding"] <= 30


# ---------------------------------------------------------------------------
# Single prediction — edge cases / validation
# ---------------------------------------------------------------------------

def test_single_prediction_invalid_station_returns_400(client):
    """An unknown station name should return HTTP 400 with a descriptive error."""
    payload = {"station": "totally_fake_station_xyz", "date": TODAY, "hour": 9}
    response = client.post("/api/predict/single", json=payload)
    assert response.status_code == 400
    assert "Unknown station" in response.json()["detail"]


def test_single_prediction_empty_station_returns_422(client):
    """An empty station name should fail Pydantic validation with 422."""
    payload = {"station": "   ", "date": TODAY, "hour": 9}
    response = client.post("/api/predict/single", json=payload)
    assert response.status_code == 422


def test_single_prediction_invalid_date_returns_422(client):
    """A non-date string should fail Pydantic validation with 422."""
    payload = {"station": "Indiranagar", "date": "not-a-date", "hour": 9}
    response = client.post("/api/predict/single", json=payload)
    assert response.status_code == 422


def test_single_prediction_date_out_of_range_returns_422(client):
    """A date outside the valid range should fail with 422."""
    payload = {"station": "Indiranagar", "date": "2099-01-01", "hour": 9}
    response = client.post("/api/predict/single", json=payload)
    assert response.status_code == 422


def test_single_prediction_hour_out_of_range_returns_422(client):
    """An hour value outside 0-23 should fail Pydantic validation."""
    payload = {"station": "Indiranagar", "date": TODAY, "hour": 25}
    response = client.post("/api/predict/single", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 24-hour forecast
# ---------------------------------------------------------------------------

def test_24h_forecast_structure(client):
    """24-hour forecast should return exactly 24 continuous hourly points."""
    payload = {"station": "Indiranagar", "date": TODAY}
    response = client.post("/api/predict/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["station"] == "Indiranagar"
    assert len(data["hourly_forecast"]) == 24
    assert data["total_daily_predicted"] > 0
    assert 0 <= data["peak_hour"] <= 23

    hours = [p["hour"] for p in data["hourly_forecast"]]
    assert hours == list(range(24))


def test_24h_forecast_invalid_station_returns_400(client):
    """Forecast with an unknown station should return HTTP 400."""
    payload = {"station": "ghost_station_99", "date": TODAY}
    response = client.post("/api/predict/forecast", json=payload)
    assert response.status_code == 400
    assert "Unknown station" in response.json()["detail"]



