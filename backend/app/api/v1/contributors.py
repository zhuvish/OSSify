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

        return [
            {
                "id": row.id,
                "username": row.username,
                "commit_count": row.commit_count
            }
            for row in rows
        ]

    finally:
        db.close()