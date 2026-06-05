from fastapi import APIRouter
from sqlalchemy import text
from backend.app.services.expertise_classifier import classify_file

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

        file_rows = db.execute(
            text("""
            SELECT DISTINCT cf.filename
            FROM commit_files cf
            JOIN commits c
                ON cf.commit_id = c.id
            WHERE c.repo_id = :repo_id
            """),
            {"repo_id": repo_id}
        ).fetchall()

        domains = set()

        # for row in file_rows:
        #     if not row.filename:
        #         continue

        #     detected = classify_file(row.filename)

        #     if detected:
        #         domains.update(detected)

        for row in file_rows:
            filename = row[0]

            if not filename:
                continue

            detected = classify_file(filename)

            if detected:
                domains.update(detected)

        topics = len(domains)

        from datetime import datetime

        # Use current server time as last_updated (deterministic for SSR)
        updated = datetime.now()

        return {
            "repositories": repositories,
            "contributors": int(contributors or 0),
            "files": int(files or 0),
            "topics": topics,
            "last_updated": updated.isoformat()
        }

    finally:
        db.close()