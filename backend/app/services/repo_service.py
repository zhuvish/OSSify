from data_pipeline.extract.fetch_commits import fetch_commits
from data_pipeline.extract.fetch_prs import fetch_prs
from data_pipeline.extract.fetch_issues import fetch_issues
from data_pipeline.extract.fetch_contributors import fetch_contributors

from data_pipeline.utils.repo_parser import parse_github_url

from data_pipeline.load.load_postgres import (
    save_repository,
    save_commits,
    save_contributors,
    save_issues,
    save_prs
)

def process_repository(repo_url: str):

    repo_name = parse_github_url(repo_url)

    contributors = fetch_contributors(repo_name)
    commits = fetch_commits(repo_name)
    prs = fetch_prs(repo_name)
    issues = fetch_issues(repo_name)

    if not commits:
        commits = []

    print("Fetching contributors...")
    print("Fetching commits...")
    print("Saving repository...")
    print("Saving contributors...")
    print("Saving commits...")

    save_contributors(contributors)
    repo_id = save_repository(repo_name, repo_url)

    save_commits(commits, repo_id=repo_id)
    save_prs(prs, repo_id=repo_id)
    save_issues(issues, repo_id=repo_id)

    return {
        "repo": repo_name,
        "commits": len(commits),
        "contributors": len(contributors),
        "prs": len(prs),
        "issues": len(issues),
    }