import os
from sqlalchemy import text
from data_pipeline.extract.fetch_repos import fetch_repo
from data_pipeline.extract.fetch_prs import fetch_prs
from data_pipeline.extract.fetch_issues import fetch_issues
from data_pipeline.extract.fetch_contributors import fetch_contributors
from data_pipeline.extract.fetch_contributor_commits import fetch_contributor_commits
from data_pipeline.extract.fetch_commit_details import fetch_commit_details

from backend.app.models.contributor import Contributor
from backend.app.db.postgres import SessionLocal

from data_pipeline.utils.repo_parser import parse_github_url

from data_pipeline.load.load_postgres import (
    save_repository,
    save_commits,
    save_contributors,
    save_commit_files,
    save_issues,
    save_prs
)

from backend.app.services.lightweight_expertise_service import compute_lightweight_expertise
from backend.app.services.expertise_service import compute_expertise
from rag_pipeline.indexing.index_contributor_documents import index_documents
from graph.builders.build_graph import build_graph

def process_repository(repo_url: str):
    try:
        print("\n========== STARTING REPO PROCESS ==========")

        repo_name = parse_github_url(repo_url)

        print("Fetching repository metadata...")
        repo_data = fetch_repo(repo_name)

        print("Fetching contributors...")
        contributors = fetch_contributors(repo_name)

        print("Saving repository...")
        repo_id = save_repository(repo_data)
        update_stage(repo_id, "fetching_metadata")

        print("Saving contributors...")
        update_stage(repo_id, "fetching_contributors")
        save_contributors(contributors)

        print("Fetching PRs...")
        update_stage(repo_id, "fetching_prs")
        prs = fetch_prs(repo_name)
        save_prs(prs, repo_id)

        print("Fetching issues...")
        update_stage(repo_id, "fetching_issues")
        issues = fetch_issues(repo_name)
        save_issues(issues, repo_id)

        print("Computing lightweight expertise...")
        update_stage(repo_id, "computing_expertise")
        compute_lightweight_expertise()

        print("Selecting active contributors for deep analysis...")

        db = SessionLocal()

        active_contributors = db.query(Contributor).filter(
            Contributor.contributions_count > 3
        ).all()

        active_contributors = [
            c for c in active_contributors
            if c.username and "bot" not in c.username.lower()
        ]

        db.close()

        print(f"Active contributors selected: {len(active_contributors)}")

        deep_commit_details = []

        for contributor in active_contributors:
            print(f"Fetching commits for {contributor.username}...")

            contributor_commits = fetch_contributor_commits(
                repo_name,
                contributor.username
            )

            if not contributor_commits:
                continue

            sampled_commits = contributor_commits[:2]

            for commit in sampled_commits:
                details = fetch_commit_details(
                    repo_name,
                    commit["sha"]
                )

                if details:
                    deep_commit_details.append(details)

        print(f"Deep commit samples collected: {len(deep_commit_details)}")

        commit_map = save_commits(deep_commit_details, repo_id)
        save_commit_files(deep_commit_details, commit_map)
        
        print("Computing deep expertise...")
        compute_expertise()

        print("Building Neo4j graph...")
        update_stage(repo_id, "building_graph")
        build_graph(repo_id)

        print("Indexing documents into Qdrant...")
        update_stage(repo_id, "building_embeddings")
        index_documents(
            os.getenv("DATABASE_URL")
        )

        print("========== PROCESS COMPLETE ==========")

    except Exception as e:
        print("\n========== PROCESS FAILED ==========")
        print(str(e))
        # Re-raise so callers (background wrapper) can detect failure and mark status appropriately
        raise

def update_stage(repo_id, stage):
    db = SessionLocal()
    try:
        db.execute(
            text("""
                UPDATE repositories
                SET processing_stage = :stage
                WHERE id = :repo_id
            """),
            {
                "repo_id": repo_id,
                "stage": stage
            }
        )
        db.commit()
    finally:
        db.close()
