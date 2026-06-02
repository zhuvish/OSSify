from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy import text

from backend.app.db.postgres import SessionLocal
from backend.app.services.repo_service import process_repository
from data_pipeline.utils.repo_parser import parse_github_url

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

    finally:
        db.close()

    # Repository not found → process it
    process_repository(repo_url)

    db = SessionLocal()

    try:
        repository = db.execute(
            text("""
                SELECT id, full_name
                FROM repositories
                WHERE full_name = :repo_name
                LIMIT 1
            """),
            {"repo_name": repo_name}
        ).first()

        if not repository:
            return {
                "status": "error",
                "message": "Repository not found after ingestion"
            }

        return {
            "status": "success",
            "repo_id": repository.id,
            "repo_name": repository.full_name,
            "repo_url": repo_url,
            "cached": False
        }

    finally:
        db.close()