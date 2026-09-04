from fastapi import APIRouter
from api.routes import stations, predict

api_router = APIRouter(prefix="/api")

api_router.include_router(stations.router)
api_router.include_router(predict.router)
