import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get(self, endpoint, params=None):
        url = f"{self.BASE_URL}/{endpoint}"

        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )

        remaining = response.headers.get("X-RateLimit-Remaining")
        print("Rate limit remaining:", remaining)

        if response.status_code != 200:
            print(f"GitHub API Error {response.status_code}")
            print(response.text)
            return None

        return response.json()

    def get_all_pages(self, endpoint, params=None, max_pages=5):
        if params is None:
            params = {}

        params["per_page"] = 100
        page = 1
        results = []

        while page <= max_pages:
            params["page"] = page

            print(f"Fetching page {page}: {endpoint}")

            data = self.get(endpoint, params=params)

            if not data or len(data) == 0:
                break

            results.extend(data)
            page += 1

        return results