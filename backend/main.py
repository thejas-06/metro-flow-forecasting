"""
FastAPI Application Entry Point
Production REST API for Namma Metro Passenger Flow Forecasting
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# Ensure backend folder is on the Python path for relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.router import api_router
from core.security import setup_security
from predictor import MetroPredictor
from schemas import HealthResponse

APP_VERSION = "2.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the ML model on startup, clean up on shutdown.
    Startup failures surface as readable errors instead of crashing at import time.
    """
    try:
        app.state.predictor = MetroPredictor()
        print(
            f"[startup] MetroPredictor loaded. "
            f"{len(app.state.predictor.get_stations())} stations indexed."
        )
    except FileNotFoundError as e:
        print(f"[startup] FATAL: Model file not found — {e}")
        raise RuntimeError(str(e)) from e

    yield

    # Cleanup (nothing needed for XGBoost, but hook is here for future use)
    print("[shutdown] API shutting down.")


app = FastAPI(
    title="Namma Metro Passenger Flow API",
    description=(
        "Production-grade ML forecasting API for Bengaluru Metro (Namma Metro). "
        "Serves XGBoost passenger flow predictions across 83+ stations."
    ),
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Apply Security (CORS, Security Headers, Rate Limiting)
setup_security(app)

# Mount modular API routers
app.include_router(api_router)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """
    Health check endpoint.
    Verifies model load status, station index count, and data file presence.
    """
    predictor = app.state.predictor
    data_file_present = os.path.exists(predictor.data_path)
    return HealthResponse(
        status="healthy",
        service="Namma Metro Passenger Flow API",
        version=APP_VERSION,
        model_loaded=predictor.model is not None,
        total_stations=len(predictor.get_stations()),
        data_file_present=data_file_present,
    )


# ---------------------------------------------------------------------------
# Frontend static serving
# ---------------------------------------------------------------------------

_frontend_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend"
)

if os.path.exists(_frontend_dir):
    app.mount("/static", StaticFiles(directory=_frontend_dir), name="static")

    @app.get("/", tags=["Frontend"], include_in_schema=False)
    def serve_frontend():
        index_file = os.path.join(_frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Namma Metro API active. Visit /docs for documentation."}


