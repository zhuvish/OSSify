from fastapi import APIRouter
from sqlalchemy import text

from backend.app.db.postgres import SessionLocal

router = APIRouter()

@router.get("/repositories/{repo_id}/contributors")
def get_contributors(repo_id: int):

    db = SessionLocal()

    try:

        rows = db.execute(
            text("""
            SELECT
                c.id,
                c.username,

                COALESCE(
                    c.contributions_count,
                    COUNT(cm.id)
                ) AS contribution_count

            FROM contributors c

            LEFT JOIN commits cm
                ON cm.contributor_id = c.id

            WHERE cm.repo_id = :repo_id

            GROUP BY
                c.id,
                c.username,
                c.contributions_count

            ORDER BY contribution_count DESC
            """),
            {"repo_id": repo_id}
        ).fetchall()

        results = []

        for row in rows:
            # aggregate expertise score for contributor (global)
            expertise_sum = db.execute(
                text("SELECT COALESCE(SUM(score),0) FROM contributor_expertise WHERE contributor_id = :cid"),
                {"cid": row.id}
            ).scalar()

            top_expertise_rows = db.execute(
                text("SELECT domain FROM contributor_expertise WHERE contributor_id = :cid ORDER BY score DESC LIMIT 5"),
                {"cid": row.id}
            ).fetchall()

            top_expertise = [r.domain for r in top_expertise_rows]

            results.append({
                "id": row.id,
                "username": row.username,
                "commit_count": int(row.contribution_count or 0),
                "expertise_score": float(expertise_sum or 0.0),
                "top_expertise": top_expertise
            })

        return results

    finally:
        db.close()


@router.get("/contributors/search")
def search_contributors(q: str):
    """Search contributors by username or display_name (partial match)."""
    db = SessionLocal()
    try:
        q_like = f"%{q}%"
        rows = db.execute(
            text("""
            SELECT
                id,
                username,
                display_name,
                avatar_url
            FROM contributors
            WHERE username ILIKE :q OR display_name ILIKE :q
            ORDER BY username
            LIMIT 50
            """),
            {"q": q_like}
        ).fetchall()

        results = []
        for row in rows:
            expertise_sum = db.execute(
                text("SELECT COALESCE(SUM(score),0) FROM contributor_expertise WHERE contributor_id = :cid"),
                {"cid": row.id}
            ).scalar()

            top_expertise_rows = db.execute(
                text("SELECT domain FROM contributor_expertise WHERE contributor_id = :cid ORDER BY score DESC LIMIT 5"),
                {"cid": row.id}
            ).fetchall()

            top_expertise = [r.domain for r in top_expertise_rows]

            results.append({
                "id": row.id,
                "username": row.username,
                "display_name": row.display_name,
                "avatar_url": row.avatar_url,
                "expertise_score": float(expertise_sum or 0.0),
                "top_expertise": top_expertise
            })

        return results

    finally:
        db.close()
