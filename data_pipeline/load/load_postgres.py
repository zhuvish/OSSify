from backend.app.db.postgres import SessionLocal
from backend.app.models.contributor import Contributor
from backend.app.models.commit import Commit
from backend.app.models.pull_request import PullRequest
from backend.app.models.issue import Issue
from backend.app.models.repository import Repository

def save_repository(repo_name, repo_url):
    db = SessionLocal()

    owner, name = repo_name.split("/")

    existing = db.query(Repository).filter_by(full_name=repo_name).first()
    if existing:
        db.close()
        return existing.id

    repo = Repository(
        name=name,
        owner=owner,
        full_name=repo_name,
        url=repo_url
    )

    db.add(repo)
    db.commit()
    db.refresh(repo)

    repo_id = repo.id
    db.close()

    return repo_id

def save_contributors(contributors_data):
    db = SessionLocal()

    for c in contributors_data:
        # avoid duplicates
        existing = db.query(Contributor).filter_by(github_id=c["id"]).first()
        if existing:
            continue

        contributor = Contributor(
            github_id=c["id"],
            username=c["login"],
            profile_url=c["html_url"],
            avatar_url=c["avatar_url"],
            contributions_count=c["contributions"]
        )
        db.add(contributor)

    db.commit()
    db.close()


def save_commits(commits_data, repo_id):
    db = SessionLocal()

    if not commits_data:
        return

    commit_objects= []

    for c in commits_data:
        if "commit" not in c or c["commit"] is None:
            continue

        commit_data = c.get("commit", {})
        author_data = commit_data.get("author") or {}

        sha = c.get("sha")

        # existing = db.query(Commit).filter_by(sha=sha).first()
        # if existing:
        #     continue

        commit = Commit(
            sha=sha,
            message=commit_data.get("message"),
            author_name=author_data.get("name"),
            author_email=author_data.get("email"),
            date=author_data.get("date"),
            repo_id=repo_id
        )

        commit_objects.append(commit)

    db.bulk_save_objects(commit_objects)
    db.commit()
    db.close()


def save_prs(prs_data, repo_id):
    db = SessionLocal()

    for pr in prs_data:
        existing = db.query(PullRequest).filter_by(pr_number=pr["number"]).first()
        if existing:
            continue

        new_pr = PullRequest(
            pr_number=pr["number"],
            title=pr["title"],
            body=pr["body"],
            state=pr["state"],
            created_at=pr["created_at"],
            closed_at=pr["closed_at"],
            repo_id=repo_id
        )
        db.add(new_pr)

    db.commit()
    db.close()


def save_issues(issues_data, repo_id):
    db = SessionLocal()

    for issue in issues_data:
        existing = db.query(Issue).filter_by(issue_number=issue["number"]).first()
        if existing:
            continue

        new_issue = Issue(
            issue_number=issue["number"],
            title=issue["title"],
            body=issue["body"],
            state=issue["state"],
            created_at=issue["created_at"],
            closed_at=issue["closed_at"],
            repo_id=repo_id
        )
        db.add(new_issue)

    db.commit()
    db.close()