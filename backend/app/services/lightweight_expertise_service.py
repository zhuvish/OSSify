from collections import defaultdict
import math

from backend.app.db.postgres import SessionLocal
from backend.app.models.pull_request import PullRequest
from backend.app.models.issue import Issue
from backend.app.models.contributor import Contributor
from backend.app.models.contributor_expertise import ContributorExpertise


KEYWORD_RULES = {
    "backend": [
        "api",
        "server",
        "auth",
        "database",
        "db",
        "middleware",
        "routing"
    ],

    "frontend": [
        "ui",
        "frontend",
        "html",
        "css",
        "react",
        "angular",
        "component",
        "template"
    ],

    "testing": [
        "test",
        "testing",
        "pytest",
        "unit test",
        "mock",
    ],

    "documentation": [
        "docs",
        "documentation",
        "doc",
        "readme",
        "tutorial"
    ],

    "devops": [
        "docker",
        "ci",
        "cd",
        "deployment",
        "infra",
        "kubernetes"
    ],

    "database": [
        "sql",
        "migration",
        "schema",
        "postgres"
    ]
}


def classify_text(text):
    text = (text or "").lower()

    matched = []

    for domain, keywords in KEYWORD_RULES.items():
        for keyword in keywords:
            if keyword in text:
                matched.append(domain)
                break

    return matched


def compute_lightweight_expertise():
    db = SessionLocal()

    db.query(ContributorExpertise).filter_by(
        source="lightweight"
    ).delete()

    db.commit()

    print("\n========== LIGHTWEIGHT EXPERTISE ==========")

    contributor_scores = defaultdict(lambda: defaultdict(int))

    # PR analysis
    prs = db.query(PullRequest).all()

    for pr in prs:
        if not pr.user_id:
            continue

        text = f"{pr.title or ''} {pr.body or ''}"

        domains = classify_text(text)

        for domain in domains:
            score = 10

            if pr.merged:
                score += 5

            contributor_scores[(pr.user_id, pr.repo_id)][domain] += score

    # Issue analysis
    issues = db.query(Issue).all()

    for issue in issues:
        if not issue.user_id:
            continue

        text = f"{issue.title or ''} {issue.labels or ''}"

        domains = classify_text(text)

        for domain in domains:
            contributor_scores[(issue.user_id, issue.repo_id)][domain] += 5

    # save
    for (contributor_id, repo_id), domains in contributor_scores.items():
        for domain, raw_score in domains.items():

            score = round(math.log1p(raw_score) * 15, 2)

            db.add(
                ContributorExpertise(
                    contributor_id=contributor_id,
                    repo_id=repo_id,
                    domain=domain,
                    score=score,
                    evidence_count=raw_score,
                    source="lightweight",
                    confidence=0.6
                )
            )

    db.commit()
    db.close()