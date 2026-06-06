from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy import text

from backend.app.db.postgres import SessionLocal
from backend.app.services.repo_service import process_repository
from backend.app.services.graph_service import GraphService
from rag_pipeline.vector_store.qdrant_client import QdrantVectorStore
from data_pipeline.utils.repo_parser import parse_github_url
from backend.app.models.repository import Repository
import threading
from collections import defaultdict
import math
from backend.app.services.expertise_classifier import classify_file
from backend.app.models.contributor import Contributor

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

        postgres_exists = existing_repo is not None

        graph = GraphService()
        neo4j_exists = graph.repository_exists(repo_name)
        graph.close()

        qdrant = QdrantVectorStore(default_collection="repo_documents")
        qdrant_exists = (
            postgres_exists
            and qdrant.repository_exists(existing_repo.id)
        )

        print(f"Postgres exists: {postgres_exists}")
        print(f"Neo4j exists: {neo4j_exists}")
        print(f"Qdrant exists: {qdrant_exists}")
        print(type(qdrant))

        needs_processing = not (
            postgres_exists
            and neo4j_exists
            and qdrant_exists
        )

        if not needs_processing:

            return {
                "status": "success",
                "repo_id": existing_repo.id,
                "repo_name": existing_repo.full_name,
                "repo_url": repo_url,
                "cached": True
            }

        # If not exists, create placeholder repository row with processing status
        if postgres_exists:
            repo_id = existing_repo.id

            # mark existing repo as processing again
            db.execute(
                text("""
                    UPDATE repositories
                    SET status = 'processing'
                    WHERE id = :repo_id
                """),
                {"repo_id": repo_id}
            )
            db.commit()

        else:
            db.execute(
                text("""
                    INSERT INTO repositories (
                        name,
                        owner,
                        full_name,
                        url,
                        status
                    )
                    VALUES (
                        :name,
                        :owner,
                        :full_name,
                        :url,
                        :status
                    )
                """),
                {
                    "name": repo_name.split("/")[-1],
                    "owner": repo_name.split("/")[0],
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

            repo_id = created.id

    finally:
        db.close()

    # Start background thread to process repository
    def _background():
        try:
            result = process_repository(repo_url)
            # If process_repository returns an error dict, mark failed
            if isinstance(result, dict) and result.get("status") == "failed":
                db3 = SessionLocal()
                try:
                    repo = db3.query(Repository).filter_by(full_name=repo_name).first()
                    if repo:
                        repo.status = "failed"
                        db3.add(repo)
                        db3.commit()
                finally:
                    db3.close()
                return

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
                SELECT id, full_name, status, processing_stage
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

        return {
            "status": status,
            "stage": row.processing_stage
        }

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

@router.get("/repositories/{repo_id}/top-experts")
def top_experts(repo_id: int):
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT cf.filename, c.contributor_id
                FROM commit_files cf
                JOIN commits c ON cf.commit_id = c.id
                WHERE c.repo_id = :repo_id AND c.contributor_id IS NOT NULL
            """),
            {"repo_id": repo_id}
        ).fetchall()

        contributor_domain_files = defaultdict(lambda: defaultdict(set))

        for row in rows:
            filename = row.filename
            contributor_id = row.contributor_id
            domains = classify_file(filename) or []

            for d in domains:
                contributor_domain_files[contributor_id][d].add(filename)

        results = []

        for contributor_id, domains in contributor_domain_files.items():
            domain_scores = {}
            total_score = 0.0
            for domain, files in domains.items():
                raw = len(files)
                score = round(math.log1p(raw) * 20, 2)
                domain_scores[domain] = score
                total_score += score

            # get username
            contributor = db.query(Contributor).filter_by(id=contributor_id).first()
            username = contributor.username if contributor else str(contributor_id)
            avatar_url = contributor.avatar_url if contributor else str(contributor_id)

            top_topics = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            top_topics = [t[0] for t in top_topics]

            results.append({
                "id": contributor_id,
                "username": username,
                "avatar_url": avatar_url,
                "score": round(total_score, 2),
                "topics": top_topics
            })

        # sort by score desc and take top 5
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

        return results

    finally:
        db.close()


@router.get("/repositories/{repo_id}/graph")
def repo_graph(repo_id: int):
    from backend.app.services.graph_service import GraphService

    graph = GraphService()
    try:
        data = graph.get_graph_for_repo(repo_id)
        return data
    finally:
        graph.close()


@router.get("/repositories/{repo_id}/topics")
def repo_topics(repo_id: int):
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT cf.filename, c.contributor_id
                FROM commit_files cf
                JOIN commits c ON cf.commit_id = c.id
                WHERE c.repo_id = :repo_id
            """),
            {"repo_id": repo_id}
        ).fetchall()

        topic_files = defaultdict(set)
        topic_contributors = defaultdict(set)

        for row in rows:
            filename = row.filename
            contributor_id = row.contributor_id
            domains = classify_file(filename) or []

            for d in domains:
                topic_files[d].add(filename)
                if contributor_id:
                    topic_contributors[d].add(contributor_id)

        result = []
        for topic, files in topic_files.items():
            raw = len(files)
            score = round(math.log1p(raw) * 20, 2)
            contributors_count = len(topic_contributors.get(topic, set()))

            result.append({
                "topic": topic,
                "score": score,
                "contributors": contributors_count
            })

        # sort by score desc
        result = sorted(result, key=lambda x: x["score"], reverse=True)

        return result

    finally:
        db.close()
