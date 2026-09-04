from fastapi import APIRouter, HTTPException, Request, status
from core.security import limiter
from schemas import (
    SinglePredictionRequest, SinglePredictionResponse,
    ForecastRequest, ForecastResponse
)

router = APIRouter(prefix="/predict", tags=["Forecasting"])

@router.post("/single", response_model=SinglePredictionResponse)
@limiter.limit("30/minute")
def predict_single_hour(request: Request, body: SinglePredictionRequest):
    """
    Predict passenger boarding volume for a single station, date, and hour.
    Returns congestion level, confidence interval, and peak-hour flag.
    """
    predictor = request.app.state.predictor
    try:
        result = predictor.predict_single(
            station=body.station,
            date_str=str(body.date),
            hour=body.hour,
            exit_count=body.exit_count,
            lag_1h=body.lag_1h,
            lag_2h=body.lag_2h,
            lag_24h=body.lag_24h
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prediction failed: {str(e)}")


@router.post("/forecast", response_model=ForecastResponse)
@limiter.limit("15/minute")
def predict_daily_forecast(request: Request, body: ForecastRequest):
    """
    Generate a full 24-hour autoregressive forecast curve for a station.
    Each hour's prediction feeds into the next as a rolling lag window.
    """
    predictor = request.app.state.predictor
    try:
        result = predictor.predict_24h_forecast(
            station=body.station,
            date_str=str(body.date),
            seed_midnight=body.seed_midnight,
            seed_11pm_prev=body.seed_11pm_prev
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Forecast failed: {str(e)}")

