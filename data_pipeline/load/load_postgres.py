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

    try:
        if not commits_data:
            return {}

        commit_map = {}

        for c in commits_data:
            if "commit" not in c:
                continue

            sha = c.get("sha")

            existing = db.query(Commit).filter_by(sha=sha).first()

            if existing:
                commit_map[sha] = existing.id
                continue

            contributor = None
            author_login = None

            if c.get("author"):
                author_login = c["author"].get("login")

            if author_login:
                contributor = db.query(Contributor).filter_by(
                    username=author_login
                ).first()

            if not contributor:
                author_name = c["commit"].get("author", {}).get("name")

                if author_name:
                    contributor = db.query(Contributor).filter(
                        Contributor.display_name.ilike(author_name)
                    ).first()

            stats = c.get("stats", {})

            commit_data = c.get("commit", {})
            author_data = commit_data.get("author") or {}

            commit_obj = Commit(
                sha=sha,
                message=commit_data.get("message"),
                author_name=author_data.get("name"),
                author_email=author_data.get("email"),
                date=parse_datetime(author_data.get("date")),
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
        return commit_map

    finally:
        db.close()


def save_commit_files(commits_data, commit_map):
    db = SessionLocal()

    try:
        for commit in commits_data:
            sha = commit.get("sha")

            if sha not in commit_map:
                continue

            commit_id = commit_map[sha]

            files = commit.get("files", [])

            for file in files:
                filename = file.get("filename")

                extension = None

                if filename and "." in filename:
                    extension = filename.split(".")[-1]

                commit_file = CommitFile(
                    commit_id=commit_id,
                    filename=filename,
                    file_extension=extension,
                    additions=file.get("additions"),
                    deletions=file.get("deletions"),
                    changes=file.get("changes"),
                    status=file.get("status")
                )

                db.add(commit_file)

        db.commit()

    finally:
        db.close()


# def save_prs(prs_data, repo_id):
#     db = SessionLocal()

#     for pr in prs_data:
#         existing = db.query(PullRequest).filter_by(
#             repo_id=repo_id,
#             pr_number=pr["number"]
#         ).first()

#         if existing:
#             continue

#         contributor = None

#         if pr.get("user"):
#             contributor = db.query(Contributor).filter_by(
#                 username=pr["user"]["login"]
#             ).first()

#         pr_obj = PullRequest(
#             pr_number=pr["number"],
#             title=pr.get("title"),
#             body=pr.get("body"),
#             state=pr.get("state"),
#             created_at=parse_datetime(pr.get("created_at")),
#             closed_at=parse_datetime(pr.get("closed_at")),
#             merged=pr.get("merged"),
#             merged_at=parse_datetime(pr.get("merged_at")),
#             comments_count=pr.get("comments"),
#             review_comments_count=pr.get("review_comments"),
#             author_login=pr["user"]["login"] if pr.get("user") else None,
#             user_id=contributor.id if contributor else None,
#             repo_id=repo_id
#         )

#         db.add(pr_obj)

#     db.commit()
#     db.close()

def save_prs(prs_data, repo_id):
    db = SessionLocal()

    try:
        for pr in prs_data:
            existing = db.query(PullRequest).filter_by(
                repo_id=repo_id,
                pr_number=pr["number"]
            ).first()

            if existing:
                continue

            contributor = None

            if pr.get("user"):
                username = pr["user"]["login"]

                contributor = db.query(Contributor).filter_by(
                    username=username
                ).first()

                # Create contributor if missing
                if contributor is None:
                    contributor = Contributor(
                        github_id=pr["user"]["id"],
                        username=username,
                        profile_url=pr["user"].get("html_url"),
                        avatar_url=pr["user"].get("avatar_url")
                    )

                    db.add(contributor)
                    db.flush()

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

    finally:
        db.close()


# def save_issues(issues_data, repo_id):
#     db = SessionLocal()

#     for issue in issues_data:
#         if "pull_request" in issue:
#             continue

#         existing = db.query(Issue).filter_by(
#             repo_id=repo_id,
#             issue_number=issue["number"]
#         ).first()

#         if existing:
#             continue

#         contributor = None

#         if issue.get("user"):
#             contributor = db.query(Contributor).filter_by(
#                 username=issue["user"]["login"]
#             ).first()

#         labels = ",".join(
#             [label["name"] for label in issue.get("labels", [])]
#         )

#         issue_obj = Issue(
#             issue_number=issue["number"],
#             title=issue.get("title"),
#             body=issue.get("body"),
#             state=issue.get("state"),
#             created_at=parse_datetime(issue.get("created_at")),
#             closed_at=parse_datetime(issue.get("closed_at")),
#             labels=labels,
#             comments_count=issue.get("comments"),
#             author_login=issue["user"]["login"] if issue.get("user") else None,
#             user_id=contributor.id if contributor else None,
#             repo_id=repo_id
#         )

#         db.add(issue_obj)

#     db.commit()
#     db.close()

def save_issues(issues_data, repo_id):
    db = SessionLocal()

    try:
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
                username = issue["user"]["login"]

                contributor = db.query(Contributor).filter_by(
                    username=username
                ).first()

                # Create contributor if missing
                if contributor is None:
                    contributor = Contributor(
                        github_id=issue["user"]["id"],
                        username=username,
                        profile_url=issue["user"].get("html_url"),
                        avatar_url=issue["user"].get("avatar_url")
                    )

                    db.add(contributor)
                    db.flush()

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

    finally:
        db.close()