from data_pipeline.extract.github_client import GitHubClient

client = GitHubClient()

def fetch_commit_details(repo_name, sha):
    endpoint = f"repos/{repo_name}/commits/{sha}"
    return client.get(endpoint)