from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy import text

from backend.app.db.postgres import SessionLocal
from backend.app.services.repo_service import process_repository
from data_pipeline.utils.repo_parser import parse_github_url
from backend.app.models.repository import Repository
import threading

router = APIRouter()


class RepoRequest(BaseModel):
    repo_url: str


@router.post("/analyze-repo")
def analyze_repo(request: RepoRequest):

    repo_url = request.repo_url
    repo_name = parse_github_url(repo_url)

    db = SessionLocal()

    try:
        # Check whether repository already exists
        existing_repo = db.execute(
            text("""
                SELECT id, full_name
                FROM repositories
                WHERE full_name = :repo_name
                LIMIT 1
            """),
            {"repo_name": repo_name}
        ).first()

        # Repository already processed
        if existing_repo:
            return {
                "status": "success",
                "repo_id": existing_repo.id,
                "repo_name": existing_repo.full_name,
                "repo_url": repo_url,
                "cached": True
            }

        # If not exists, create placeholder repository row with processing status
        insert = db.execute(
            text("""
                INSERT INTO repositories (name, owner, full_name, url, status)
                VALUES (:name, :owner, :full_name, :url, :status)
            """),
            {
                "name": repo_name.split('/')[-1],
                "owner": repo_name.split('/')[0],
                "full_name": repo_name,
                "url": repo_url,
                "status": "processing"
            }
        )
        db.commit()

        created = db.execute(
            text("""
                SELECT id, full_name
                FROM repositories
                WHERE full_name = :repo_name
                LIMIT 1
            """),
            {"repo_name": repo_name}
        ).first()

        repo_id = created.id if created else None

    finally:
        db.close()

    # Start background thread to process repository
    def _background():
        try:
            process_repository(repo_url)
            # mark repository as ready
            db2 = SessionLocal()
            try:
                repo = db2.query(Repository).filter_by(full_name=repo_name).first()
                if repo:
                    repo.status = "ready"
                    db2.add(repo)
                    db2.commit()
            finally:
                db2.close()
        except Exception as e:
            db3 = SessionLocal()
            try:
                repo = db3.query(Repository).filter_by(full_name=repo_name).first()
                if repo:
                    repo.status = "failed"
                    db3.add(repo)
                    db3.commit()
            finally:
                db3.close()

    thread = threading.Thread(target=_background, daemon=True)
    thread.start()

    return {
        "status": "processing",
        "repo_id": repo_id,
        "repo_name": repo_name,
        "repo_url": repo_url,
        "cached": False
    }


@router.get("/repositories/{repo_id}/status")
def repository_status(repo_id: int):
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT id, full_name, status
                FROM repositories
                WHERE id = :repo_id
                LIMIT 1
            """),
            {"repo_id": repo_id}
        ).first()

        if not row:
            return {"status": "not_found"}

        # Normalize status
        status = row.status or "ready"

        return {"status": status}

    finally:
        db.close()


@router.get("/repositories")
def list_repositories():
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT
                    r.id,
                    r.full_name,
                    r.url,
                    COALESCE((SELECT COUNT(DISTINCT contributor_id) FROM commits WHERE repo_id = r.id), 0) AS contributors,
                    COALESCE((SELECT COUNT(*) FROM commits WHERE repo_id = r.id), 0) AS commits,
                    COALESCE((SELECT COUNT(*) FROM issues WHERE repo_id = r.id), 0) AS issues
                FROM repositories r
                ORDER BY r.id DESC
            """)
        ).fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row.id,
                "name": row.full_name,
                "url": row.url,
                "contributors": int(row.contributors),
                "commits": int(row.commits),
                "issues": int(row.issues)
            })

        return result

    finally:
        db.close()