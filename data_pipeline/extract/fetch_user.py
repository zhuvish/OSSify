from data_pipeline.extract.github_client import GitHubClient

client = GitHubClient()

def fetch_user(username):
    endpoint = f"users/{username}"
    return client.get(endpoint)