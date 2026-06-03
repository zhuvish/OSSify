from fastapi import APIRouter
from typing import Optional

from backend.app.services.expert_retrieval_service import get_contributor_profile

router = APIRouter()


@router.get("/contributors/{contributor_id}")
def contributor_detail(contributor_id: int):
    profile = get_contributor_profile(contributor_id)
    if not profile:
        return {"error": "Contributor not found"}
    return profile
