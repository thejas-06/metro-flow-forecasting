"""
Pydantic Schemas — Namma Metro Passenger Flow Prediction API
Strict validation for all request/response contracts.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date as DateType


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_VALID_DATE_MIN = DateType(2020, 1, 1)
_VALID_DATE_MAX = DateType(2027, 12, 31)


def _validate_date(v: DateType) -> DateType:
    if v < _VALID_DATE_MIN or v > _VALID_DATE_MAX:
        raise ValueError(
            f"Date must be between {_VALID_DATE_MIN} and {_VALID_DATE_MAX}."
        )
    return v


def _validate_station(v: str) -> str:
    v_clean = v.strip()
    if not v_clean:
        raise ValueError("Station name cannot be empty.")
    if len(v_clean) > 120:
        raise ValueError("Station name is too long (max 120 characters).")
    return v_clean


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class ConfidenceInterval(BaseModel):
    """95% confidence band around the point prediction."""
    lower_bound: float
    upper_bound: float
    confidence_level: str = "95%"


# ---------------------------------------------------------------------------
# Single-hour prediction
# ---------------------------------------------------------------------------

class SinglePredictionRequest(BaseModel):
    """Request schema: predict passenger boarding for one station + hour."""

    station: str = Field(
        ...,
        description="Exact Namma Metro station name as stored in the dataset.",
        examples=["Nadaprabhu Kempegowda Station, Majestic"]
    )
    date: DateType = Field(
        ...,
        description="Target date (YYYY-MM-DD). Must be between 2020-01-01 and 2027-12-31.",
        examples=["2025-09-25"]
    )
    hour: int = Field(
        ...,
        ge=0,
        le=23,
        description="Hour of day (0 = midnight, 23 = 11 PM).",
        examples=[9]
    )
    exit_count: Optional[int] = Field(
        default=None,
        ge=0,
        le=50_000,
        description="Observed exit count for the hour (auto-estimated if omitted).",
        examples=[350]
    )
    lag_1h: Optional[float] = Field(
        default=None,
        ge=0,
        le=100_000,
        description="Boarding count 1 hour prior (auto-estimated if omitted).",
        examples=[1200.0]
    )
    lag_2h: Optional[float] = Field(
        default=None,
        ge=0,
        le=100_000,
        description="Boarding count 2 hours prior (auto-estimated if omitted).",
        examples=[950.0]
    )
    lag_24h: Optional[float] = Field(
        default=None,
        ge=0,
        le=100_000,
        description="Boarding count at same hour yesterday (auto-estimated if omitted).",
        examples=[1150.0]
    )

    @field_validator("station")
    @classmethod
    def validate_station(cls, v: str) -> str:
        return _validate_station(v)

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: DateType) -> DateType:
        return _validate_date(v)


class SinglePredictionResponse(BaseModel):
    """Response: single-hour prediction result (no internal model features exposed)."""
    station: str
    date: str
    hour: int
    time_label: str
    predicted_boarding: int
    congestion_level: str
    congestion_color: str
    is_peak_hour: bool
    is_weekend: bool
    station_avg_traffic: float
    confidence_interval: ConfidenceInterval


# ---------------------------------------------------------------------------
# 24-hour forecast
# ---------------------------------------------------------------------------

class ForecastRequest(BaseModel):
    """Request schema: generate a full 24-hour autoregressive forecast curve."""

    station: str = Field(
        ...,
        description="Target Namma Metro station name.",
        examples=["Nadaprabhu Kempegowda Station, Majestic"]
    )
    date: DateType = Field(
        ...,
        description="Target date (YYYY-MM-DD). Must be between 2020-01-01 and 2027-12-31.",
        examples=["2025-09-25"]
    )
    seed_midnight: Optional[float] = Field(
        default=0.0,
        ge=0,
        le=100_000,
        description="Optional seed for Hour 0 (midnight) boarding count."
    )
    seed_11pm_prev: Optional[float] = Field(
        default=0.0,
        ge=0,
        le=100_000,
        description="Optional seed for 11 PM of the previous day."
    )

    @field_validator("station")
    @classmethod
    def validate_station(cls, v: str) -> str:
        return _validate_station(v)

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: DateType) -> DateType:
        return _validate_date(v)


class HourlyForecastPoint(BaseModel):
    """One data point in the 24-hour forecast timeline."""
    hour: int
    time_label: str
    predicted_boarding: int
    is_peak_hour: bool
    congestion_level: str
    congestion_color: str
    exit_estimate: int


class ForecastResponse(BaseModel):
    """Response: full 24-hour forecast with summary KPIs."""
    station: str
    date: str
    day_name: str
    is_weekend: bool
    total_daily_predicted: int
    peak_hour: int
    peak_time_label: str
    peak_passengers: int
    average_hourly_passengers: int
    hourly_forecast: List[HourlyForecastPoint]


# ---------------------------------------------------------------------------
# Stations
# ---------------------------------------------------------------------------

class StationInfo(BaseModel):
    """Metadata for one Namma Metro station."""
    name: str
    avg_hourly_traffic: float
    traffic_tier: str
    estimated_daily_traffic: int


class StationsResponse(BaseModel):
    """Response: full station directory with aggregate metrics."""
    total_stations: int
    stations: List[StationInfo]


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """System health check response."""
    status: str
    service: str
    version: str
    model_loaded: bool
    total_stations: int
    data_file_present: bool

