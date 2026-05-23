from fastapi import APIRouter
from backend.app.db.postgres import SessionLocal
from backend.app.models.contributor import Contributor
from backend.app.models.contributor_expertise import ContributorExpertise

router = APIRouter()


@router.get("/contributors/expertise")
def get_expertise():
    db = SessionLocal()

    results = []

    contributors = db.query(Contributor).all()

    for contributor in contributors:
        expertise_rows = db.query(
            ContributorExpertise
        ).filter_by(
            contributor_id=contributor.id
        ).all()

        if not expertise_rows:
            continue

        expertise = []

        for row in expertise_rows:
            expertise.append({
                "domain": row.domain,
                "score": row.score,
                "evidence_count": row.evidence_count
            })

        results.append({
            "contributor_id": contributor.id,
            "username": contributor.username,
            "avatar_url": contributor.avatar_url,
            "expertise": expertise
        })

    db.close()

    return results