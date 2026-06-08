from fastapi import APIRouter
from typing import Optional

from backend.app.services.expert_retrieval_service import get_contributor_profile

router = APIRouter()


@router.get("/contributors/{contributor_id}/profile")
def contributor_profile(contributor_id: int):

    profile = get_contributor_profile(contributor_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Contributor not found"
        )

    return profile