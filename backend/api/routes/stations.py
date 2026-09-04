from fastapi import APIRouter, Request
from core.security import limiter
from schemas import StationsResponse, StationInfo

router = APIRouter(prefix="/stations", tags=["Stations"])

@router.get("", response_model=StationsResponse)
@limiter.limit("60/minute")
def get_stations(request: Request):
    """Retrieve all Namma Metro stations with average traffic tiers and daily estimates."""
    predictor = request.app.state.predictor
    stations_data = predictor.get_stations()
    return StationsResponse(
        total_stations=len(stations_data),
        stations=[StationInfo(**s) for s in stations_data]
    )
