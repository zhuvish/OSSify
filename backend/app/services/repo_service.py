from data_pipeline.extract.fetch_repos import fetch_repo
from data_pipeline.extract.fetch_commits import fetch_commits
from data_pipeline.extract.fetch_prs import fetch_prs
from data_pipeline.extract.fetch_issues import fetch_issues
from data_pipeline.extract.fetch_contributors import fetch_contributors
from data_pipeline.extract.fetch_commit_details import fetch_commit_details
from data_pipeline.extract.fetch_user import fetch_user

from data_pipeline.utils.repo_parser import parse_github_url

from data_pipeline.load.load_postgres import (
    save_repository,
    save_commits,
    save_contributors,
    save_commit_files,
    save_issues,
    save_prs
)

from backend.app.services.expertise_service import compute_expertise

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

        print("Saving contributors...")
        save_contributors(contributors)

        print("Fetching commits...")
        commits = fetch_commits(repo_name)

        enriched_commits = []

        for c in commits[:50]:
            details = fetch_commit_details(repo_name, c["sha"])

            if details:
                c["details"] = details

            enriched_commits.append(c)

        print("Saving commits...")
        commit_map = save_commits(enriched_commits, repo_id)

        print("Saving commit files...")
        save_commit_files(enriched_commits, commit_map)

        print("Fetching PRs...")
        prs = fetch_prs(repo_name)
        save_prs(prs, repo_id)

        print("Fetching issues...")
        issues = fetch_issues(repo_name)
        save_issues(issues, repo_id)

        print("Computing expertise...")
        compute_expertise()

        print("========== PROCESS COMPLETE ==========")

    except Exception as e:

        print("\n========== PROCESS FAILED ==========")
        print("ERROR IN PROCESS_REPOSITORY:")
        print(str(e))
        print("====================================\n")

        return {
            "status": "failed",
            "error": str(e)
        }