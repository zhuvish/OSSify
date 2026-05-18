from datetime import datetime
import os

from backend.app.db.postgres import SessionLocal

from backend.app.models.contributor import Contributor
from backend.app.models.commit import Commit
from backend.app.models.commit_file import CommitFile
from backend.app.models.pull_request import PullRequest
from backend.app.models.issue import Issue
from backend.app.models.repository import Repository

def parse_datetime(dt_str):
    if not dt_str:
        return None

    return datetime.fromisoformat(
        dt_str.replace("Z", "+00:00")
    )


def save_repository(repo_data):
    db = SessionLocal()

    existing = db.query(Repository).filter_by(
        full_name=repo_data["full_name"]
    ).first()

    if existing:
        db.close()
        return existing.id

    repo = Repository(
        name=repo_data["name"],
        owner=repo_data["owner"]["login"],
        full_name=repo_data["full_name"],
        url=repo_data["html_url"],
        description=repo_data.get("description"),
        primary_language=repo_data.get("language"),
        stars=repo_data.get("stargazers_count"),
        forks=repo_data.get("forks_count"),
        open_issues_count=repo_data.get("open_issues_count"),
        default_branch=repo_data.get("default_branch"),
        github_created_at=parse_datetime(repo_data.get("created_at")),
        github_updated_at=parse_datetime(repo_data.get("updated_at")),
    )

    db.add(repo)
    db.commit()
    db.refresh(repo)
    db.close()

    return repo.id


def save_contributors(contributors_data):
    db = SessionLocal()

    if not contributors_data:
        db.close()
        return

    contributor_objects = []

    for c in contributors_data:
        existing = db.query(Contributor).filter_by(github_id=c["id"]).first()
        if existing:
            continue

        contributor = Contributor(
            github_id=c["id"],
            username=c["login"],
            profile_url=c.get("html_url"),
            avatar_url=c.get("avatar_url"),
            contributions_count=c.get("contributions"),
            display_name=c.get("name"),
            bio=c.get("bio"),
            company=c.get("company"),
            location=c.get("location"),
            followers=c.get("followers"),
            public_repos=c.get("public_repos"),
            github_created_at=parse_datetime(c.get("created_at"))
        )
        contributor_objects.append(contributor)
    
    db.bulk_save_objects(contributor_objects)

    db.commit()
    db.close()


def save_commits(commits_data, repo_id):
    db = SessionLocal()

    commit_map = {}

    for c in commits_data:
        sha = c["sha"]

        existing = db.query(Commit).filter_by(
            sha=sha
        ).first()

        if existing:
            commit_map[sha] = existing.id
            continue

        author_login = None

        if c.get("author"):
            author_login = c["author"].get("login")

        contributor = None

        if author_login:
            contributor = db.query(Contributor).filter_by(
                username=author_login
            ).first()

        commit_details = c.get("details", {})

        stats = commit_details.get("stats", {})

        commit_obj = Commit(
            sha=sha,
            message=c["commit"]["message"],
            author_name=c["commit"]["author"]["name"],
            author_email=c["commit"]["author"]["email"],
            date=parse_datetime(c["commit"]["author"]["date"]),
            additions=stats.get("additions"),
            deletions=stats.get("deletions"),
            total_changes=stats.get("total"),
            commit_url=c.get("html_url"),
            repo_id=repo_id,
            contributor_id=contributor.id if contributor else None
        )

        db.add(commit_obj)
        db.flush()

        commit_map[sha] = commit_obj.id

    db.commit()
    db.close()

    return commit_map


def save_commit_files(commits_data, commit_map):
    db = SessionLocal()

    for c in commits_data:
        sha = c["sha"]

        commit_id = commit_map.get(sha)

        if not commit_id:
            continue

        files = c.get("details", {}).get("files", [])

        for f in files:
            existing = db.query(CommitFile).filter_by(
                commit_id=commit_id,
                filename=f["filename"]
            ).first()

            if existing:
                continue

            ext = None

            if "." in f["filename"]:
                ext = f["filename"].split(".")[-1]

            file_obj = CommitFile(
                commit_id=commit_id,
                filename=f["filename"],
                file_extension=ext,
                additions=f.get("additions"),
                deletions=f.get("deletions"),
                changes=f.get("changes"),
                status=f.get("status")
            )

            db.add(file_obj)

    db.commit()
    db.close()


def save_prs(prs_data, repo_id):
    db = SessionLocal()

    for pr in prs_data:
        existing = db.query(PullRequest).filter_by(
            repo_id=repo_id,
            pr_number=pr["number"]
        ).first()

        if existing:
            continue

        contributor = None

        if pr.get("user"):
            contributor = db.query(Contributor).filter_by(
                username=pr["user"]["login"]
            ).first()

        pr_obj = PullRequest(
            pr_number=pr["number"],
            title=pr.get("title"),
            body=pr.get("body"),
            state=pr.get("state"),
            created_at=parse_datetime(pr.get("created_at")),
            closed_at=parse_datetime(pr.get("closed_at")),
            merged=pr.get("merged"),
            merged_at=parse_datetime(pr.get("merged_at")),
            comments_count=pr.get("comments"),
            review_comments_count=pr.get("review_comments"),
            author_login=pr["user"]["login"] if pr.get("user") else None,
            user_id=contributor.id if contributor else None,
            repo_id=repo_id
        )

        db.add(pr_obj)

    db.commit()
    db.close()


def save_issues(issues_data, repo_id):
    db = SessionLocal()

    for issue in issues_data:
        if "pull_request" in issue:
            continue

        existing = db.query(Issue).filter_by(
            repo_id=repo_id,
            issue_number=issue["number"]
        ).first()

        if existing:
            continue

        contributor = None

        if issue.get("user"):
            contributor = db.query(Contributor).filter_by(
                username=issue["user"]["login"]
            ).first()

        labels = ",".join(
            [label["name"] for label in issue.get("labels", [])]
        )

        issue_obj = Issue(
            issue_number=issue["number"],
            title=issue.get("title"),
            body=issue.get("body"),
            state=issue.get("state"),
            created_at=parse_datetime(issue.get("created_at")),
            closed_at=parse_datetime(issue.get("closed_at")),
            labels=labels,
            comments_count=issue.get("comments"),
            author_login=issue["user"]["login"] if issue.get("user") else None,
            user_id=contributor.id if contributor else None,
            repo_id=repo_id
        )

        db.add(issue_obj)

    db.commit()
    db.close()