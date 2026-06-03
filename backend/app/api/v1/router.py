from fastapi import APIRouter
from backend.app.api.v1.endpoints import repository
from backend.app.api.v1.endpoints import expertise
from backend.app.api.v1.endpoints import experts
from backend.app.api.v1 import contributors_detail

api_router = APIRouter()
api_router.include_router(repository.router)
api_router.include_router(expertise.router)
api_router.include_router(experts.router)
api_router.include_router(contributors_detail.router)
