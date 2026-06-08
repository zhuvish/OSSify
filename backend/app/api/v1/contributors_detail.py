from fastapi import APIRouter
from typing import Optional

from backend.app.services.expert_retrieval_service import get_contributor_profile

router = APIRouter()



@router.get("/contributors/{contributor_id}/profile", response_model=ContributorProfileResponse)
def contributor_profile(contributor_id: int):
    """Get a detailed contributor profile with expertise, repositories, files, activity, and semantic summary.

    Data sources:
      - **PostgreSQL**: contributor info, expertise areas, commits/PRs/issues counts, repositories, files
      - **Qdrant**: semantic expertise summary (thematic keywords extracted from vector search)
    """
    logger.info("Contributor profile requested: contributor_id=%d", contributor_id)
    try:
        profile = get_contributor_profile(contributor_id)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Contributor {contributor_id} not found")
        return ContributorProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Profile fetch failed for contributor_id=%d", contributor_id)
        raise HTTPException(status_code=500, detail=f"Profile error: {exc}")
