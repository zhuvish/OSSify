from fastapi import APIRouter
from sqlalchemy import text

from backend.app.db.postgres import SessionLocal

router = APIRouter()


@router.get("/repositories/{repo_id}/dashboard")
def get_dashboard_stats(repo_id: int):

    db = SessionLocal()

    try:

        repositories = 1

        contributors = db.execute(
            text("""
            SELECT COUNT(DISTINCT contributor_id)
            FROM commits
            WHERE repo_id = :repo_id
            """),
            {"repo_id": repo_id}
        ).scalar()

        files = db.execute(
            text("""
            SELECT COUNT(DISTINCT cf.filename)
            FROM commit_files cf
            JOIN commits c
                ON cf.commit_id = c.id
            WHERE c.repo_id = :repo_id
            """),
            {"repo_id": repo_id}
        ).scalar()

        updated = db.execute(
            text("""
            SELECT github_updated_at
            FROM repositories
            WHERE id = :repo_id
            LIMIT 1
            """),
            {"repo_id": repo_id}
        ).scalar()

        return {
            "repositories": repositories,
            "contributors": int(contributors or 0),
            "files": int(files or 0),
            "topics": 0,
            "last_updated": updated.isoformat() if updated else None
        }

    finally:
        db.close()