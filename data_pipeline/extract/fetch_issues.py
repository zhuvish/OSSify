from data_pipeline.extract.github_client import GitHubClient

client = GitHubClient()

def fetch_issues(repo_name):
    endpoint = f"repos/{repo_name}/issues"

    params = {"state": "all"}

    issues = client.get_all_pages(
        endpoint,
        params={"state": "all"},
        max_pages=3
    )

    issues = [issue for issue in issues if "pull_request" not in issue]

    return issues