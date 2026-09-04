"""
Production Predictor Engine
Encapsulates model loading, feature transformations, confidence bounds, and autoregressive forecasting.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Tuned Model RMSE from Notebook 04 benchmark
MODEL_RMSE = 82.40

# Feature columns required by the model in exact order
MODEL_FEATURES = [
    'Hour', 'Hour_Sin', 'Hour_Cos', 'DayOfWeek', 'Day_Sin', 'Day_Cos', 'DayOfMonth',
    'WeekOfYear', 'Is_Weekend', 'Is_Morning_Peak', 'Is_Evening_Peak',
    'Is_Peak_Hour', 'Exit_Count', 'Lag_1h', 'Lag_2h', 'Lag_24h', 'Rolling_3h',
    'Rolling_3h_Std', 'Station_AvgTraffic'
]

DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


class MetroPredictor:
    """Predictor service for Namma Metro passenger flow."""

    def __init__(self, model_path: str = "models/xgboost_tuned_model.pkl", data_path: str = "data/metro_processed.csv"):
        self.model_path = model_path
        self.data_path = data_path
        self.model = None
        self.station_avg_map: Dict[str, float] = {}
        self.stations_list: List[Dict] = []
        self._initialize()

    def _initialize(self):
        """Loads the trained model and computes station baselines."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Trained model not found at {self.model_path}. Please run Notebook 04.")

        self.model = joblib.load(self.model_path)

        # Precompute station averages from processed data
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path, usecols=['Station', 'Boarding_Count'])
            avg_series = df.groupby('Station')['Boarding_Count'].mean().round(2)
            self.station_avg_map = avg_series.to_dict()
        else:
            # Fallback default stations if data file not present
            self.station_avg_map = {"Kempegowda Station Majestic": 2450.0, "Indiranagar": 1200.0, "MG Road": 1350.0}

        # Build stations metadata list
        for station_name, avg_traffic in sorted(self.station_avg_map.items()):
            if avg_traffic >= 1500:
                tier = "Major Hub / Interchange"
            elif avg_traffic >= 750:
                tier = "High Volume Commercial"
            elif avg_traffic >= 300:
                tier = "Moderate Volume Residential"
            else:
                tier = "Low Volume Feeder / Suburb"

            self.stations_list.append({
                "name": station_name,
                "avg_hourly_traffic": float(avg_traffic),
                "traffic_tier": tier,
                "estimated_daily_traffic": int(avg_traffic * 18)  # ~18 operational hours
            })

    def get_stations(self) -> List[Dict]:
        """Returns all available stations with metadata."""
        return self.stations_list

    def get_station_avg(self, station: str) -> float:
        """Returns baseline average traffic for a given station."""
        return self.station_avg_map.get(station, 500.0)

    @staticmethod
    def get_time_label(hour: int) -> str:
        """Formats 0-23 hour into a clean 12-hour AM/PM label."""
        if hour == 0:
            return "12:00 AM (Midnight)"
        elif hour < 12:
            return f"{hour:02d}:00 AM"
        elif hour == 12:
            return "12:00 PM (Noon)"
        else:
            return f"{hour-12:02d}:00 PM"

    @staticmethod
    def determine_congestion(predicted_pax: int, avg_traffic: float) -> Tuple[str, str]:
        """Classifies traffic flow into congestion levels with badge colors."""
        ratio = predicted_pax / max(avg_traffic, 50.0)
        if ratio >= 2.5:
            return "CRITICAL SURGE", "#EF4444"  # Red
        elif ratio >= 1.8:
            return "HEAVY CONGESTION", "#F97316"  # Orange
        elif ratio >= 1.2:
            return "MODERATE TRAFFIC", "#EAB308"  # Yellow
        else:
            return "NORMAL / CLEAR", "#22C55E"  # Green

    def build_feature_dict(
        self,
        hour: int,
        day_of_week: int,
        day_of_month: int,
        week_of_year: int,
        station_avg: float,
        exit_count: float,
        lag_1h: float,
        lag_2h: float,
        lag_24h: float,
        rolling_3h: float,
        rolling_3h_std: float,
    ) -> Dict[str, float]:
        """Constructs the exact 19 feature vector expected by the model."""
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        day_sin = np.sin(2 * np.pi * day_of_week / 7)
        day_cos = np.cos(2 * np.pi * day_of_week / 7)

        is_weekend = 1 if day_of_week in [5, 6] else 0
        is_morning_peak = 1 if (8 <= hour <= 10 and not is_weekend) else 0
        is_evening_peak = 1 if (17 <= hour <= 20 and not is_weekend) else 0
        is_peak_hour = 1 if (is_morning_peak or is_evening_peak) else 0

        return {
            'Hour': float(hour),
            'Hour_Sin': float(hour_sin),
            'Hour_Cos': float(hour_cos),
            'DayOfWeek': float(day_of_week),
            'Day_Sin': float(day_sin),
            'Day_Cos': float(day_cos),
            'DayOfMonth': float(day_of_month),
            'WeekOfYear': float(week_of_year),
            'Is_Weekend': float(is_weekend),
            'Is_Morning_Peak': float(is_morning_peak),
            'Is_Evening_Peak': float(is_evening_peak),
            'Is_Peak_Hour': float(is_peak_hour),
            'Exit_Count': float(exit_count),
            'Lag_1h': float(lag_1h),
            'Lag_2h': float(lag_2h),
            'Lag_24h': float(lag_24h),
            'Rolling_3h': float(rolling_3h),
            'Rolling_3h_Std': float(rolling_3h_std),
            'Station_AvgTraffic': float(station_avg),
        }

    def predict_single(
        self,
        station: str,
        date_str: str,
        hour: int,
        exit_count: Optional[int] = None,
        lag_1h: Optional[float] = None,
        lag_2h: Optional[float] = None,
        lag_24h: Optional[float] = None
    ) -> Dict:
        """Performs a single-hour passenger boarding prediction."""
        # Validate station exists in dataset
        if station not in self.station_avg_map:
            known = list(self.station_avg_map.keys())[:5]
            raise ValueError(
                f"Unknown station: '{station}'. "
                f"Use GET /api/stations to see valid names. "
                f"Example: '{known[0]}'"
            )
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        dow = dt.weekday()
        dom = dt.day
        woy = dt.isocalendar()[1]
        station_avg = self.get_station_avg(station)

        # Default heuristic estimates if lags not provided
        l1 = lag_1h if lag_1h is not None else (station_avg * 0.8 if 6 <= hour <= 22 else 0.0)
        l2 = lag_2h if lag_2h is not None else (station_avg * 0.7 if 6 <= hour <= 22 else 0.0)
        l24 = lag_24h if lag_24h is not None else (station_avg if 6 <= hour <= 22 else 0.0)
        ex = exit_count if exit_count is not None else int(l1 * 0.9)

        r3 = (l1 + l2 + l24) / 3.0
        r3_std = float(np.std([l1, l2, l24]))

        features = self.build_feature_dict(
            hour=hour,
            day_of_week=dow,
            day_of_month=dom,
            week_of_year=woy,
            station_avg=station_avg,
            exit_count=ex,
            lag_1h=l1,
            lag_2h=l2,
            lag_24h=l24,
            rolling_3h=r3,
            rolling_3h_std=r3_std
        )

        # Predict using DataFrame with exact column ordering
        df_in = pd.DataFrame([features])[MODEL_FEATURES]
        raw_pred = float(self.model.predict(df_in)[0])
        pred_clean = max(0, int(round(raw_pred)))

        # Late night closure threshold (metro closed 1 AM - 4 AM)
        if hour in [1, 2, 3]:
            pred_clean = min(pred_clean, 25)

        congestion_level, congestion_color = self.determine_congestion(pred_clean, station_avg)

        # 95% Confidence bounds (+/- 1.96 * RMSE)
        lower_bound = max(0.0, round(pred_clean - 1.96 * MODEL_RMSE, 1))
        upper_bound = round(pred_clean + 1.96 * MODEL_RMSE, 1)

        return {
            "station": station,
            "date": date_str,
            "hour": hour,
            "time_label": self.get_time_label(hour),
            "predicted_boarding": pred_clean,
            "congestion_level": congestion_level,
            "congestion_color": congestion_color,
            "is_peak_hour": bool(features['Is_Peak_Hour']),
            "is_weekend": bool(features['Is_Weekend']),
            "station_avg_traffic": station_avg,
            "confidence_interval": {
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "confidence_level": "95%"
            }
            # Note: internal feature vector intentionally omitted from public response
        }

    def predict_24h_forecast(
        self,
        station: str,
        date_str: str,
        seed_midnight: float = 0.0,
        seed_11pm_prev: float = 0.0
    ) -> Dict:
        """
        Executes a 24-hour autoregressive forecasting chain.
        Each hour's prediction feeds into the next hour's lag window.
        """
        # Validate station exists in dataset
        if station not in self.station_avg_map:
            known = list(self.station_avg_map.keys())[:5]
            raise ValueError(
                f"Unknown station: '{station}'. "
                f"Use GET /api/stations to see valid names. "
                f"Example: '{known[0]}'"
            )

        dt = datetime.strptime(date_str, "%Y-%m-%d")
        dow = dt.weekday()
        dom = dt.day
        woy = dt.isocalendar()[1]
        station_avg = self.get_station_avg(station)
        is_weekend = (dow in [5, 6])

        # Buffer: index 0 is 11 PM prev day, index 1 is midnight (Hour 0)
        buffer = [seed_11pm_prev, seed_midnight]
        hourly_results = []
        total_passengers = 0
        peak_hour = 0
        peak_passengers = -1

        for h in range(24):
            l1 = buffer[-1]  # Previous hour prediction
            l2 = buffer[-2]  # Two hours ago prediction

            # Historical 24h baseline approximation
            if is_weekend:
                l24 = station_avg * (0.1 if h < 6 else (0.8 if h < 12 else (1.1 if 16 <= h <= 20 else 0.4)))
            else:
                l24 = station_avg * (0.05 if h < 5 else (1.8 if 8 <= h <= 10 else (2.1 if 17 <= h <= 20 else 0.7)))

            # Estimated exit count (exits lag boardings slightly)
            exit_est = int(l1 * 0.85 if h >= 6 else 0)
            r3 = (l1 + l2 + l24) / 3.0
            r3_std = float(np.std([l1, l2, l24]))

            feats = self.build_feature_dict(
                hour=h,
                day_of_week=dow,
                day_of_month=dom,
                week_of_year=woy,
                station_avg=station_avg,
                exit_count=exit_est,
                lag_1h=l1,
                lag_2h=l2,
                lag_24h=l24,
                rolling_3h=r3,
                rolling_3h_std=r3_std
            )

            df_in = pd.DataFrame([feats])[MODEL_FEATURES]
            pred = max(0, int(round(self.model.predict(df_in)[0])))

            # Operational night hours adjustment
            if h in [1, 2, 3]:
                pred = min(pred, 20)

            buffer.append(float(pred))
            total_passengers += pred

            if pred > peak_passengers:
                peak_passengers = pred
                peak_hour = h

            cong_level, cong_color = self.determine_congestion(pred, station_avg)

            hourly_results.append({
                "hour": h,
                "time_label": self.get_time_label(h),
                "predicted_boarding": pred,
                "is_peak_hour": bool(feats['Is_Peak_Hour']),
                "congestion_level": cong_level,
                "congestion_color": cong_color,
                "exit_estimate": exit_est
            })

        return {
            "station": station,
            "date": date_str,
            "day_name": DAY_NAMES[dow],
            "is_weekend": is_weekend,
            "total_daily_predicted": total_passengers,
            "peak_hour": peak_hour,
            "peak_time_label": self.get_time_label(peak_hour),
            "peak_passengers": peak_passengers,
            "average_hourly_passengers": int(total_passengers / 24),
            "hourly_forecast": hourly_results
        }


# Singleton instance for fast API serving
predictor_instance = MetroPredictor()
