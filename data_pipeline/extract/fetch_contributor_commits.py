from data_pipeline.extract.github_client import GitHubClient

client = GitHubClient()


def fetch_contributor_commits(repo_name, contributor_username):
    endpoint = f"repos/{repo_name}/commits"

    commits = client.get(
        endpoint,
        params={
            "author": contributor_username,
            "per_page": 5
        }
    )

    if not commits:
        return []

    return commits