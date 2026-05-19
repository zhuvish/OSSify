from fastapi import APIRouter
from backend.app.api.v1.endpoints import repository
from backend.app.api.v1.endpoints import expertise

api_router = APIRouter()
api_router.include_router(repository.router)
api_router.include_router(expertise.router)