import math
from collections import defaultdict

from backend.app.db.postgres import SessionLocal
from backend.app.models.commit import Commit
from backend.app.models.commit_file import CommitFile
from backend.app.models.contributor_expertise import ContributorExpertise

from backend.app.services.expertise_classifier import classify_file


def compute_expertise():
    db = SessionLocal()

    print("\n========== STARTING EXPERTISE COMPUTATION ==========")

    db.query(ContributorExpertise).filter_by(
        source="deep"
    ).delete()
    db.commit()

    commits = db.query(Commit).all()
    commit_files = db.query(CommitFile).all()

    commit_lookup = {}

    for commit in commits:
        commit_lookup[commit.id] = {
            "contributor_id": commit.contributor_id,
            "repo_id": commit.repo_id,
        }

    contributor_domain_files = defaultdict(
        lambda: defaultdict(set)
    )

    for file in commit_files:
        commit_info = commit_lookup.get(file.commit_id)

        if not commit_info:
            continue

        contributor_id = commit_info["contributor_id"]
        repo_id = commit_info["repo_id"]

        domains = classify_file(file.filename)

        for domain in domains:
            contributor_domain_files[(contributor_id, repo_id)][domain].add(file.filename)

    for (contributor_id, repo_id), domains in contributor_domain_files.items():
        for domain, files in domains.items():

            raw_score = len(files)

            score = round(math.log1p(raw_score) * 20, 2)

            db.add(
                ContributorExpertise(
                    contributor_id=contributor_id,
                    repo_id=repo_id,
                    domain=domain,
                    score=score,
                    evidence_count=raw_score,
                    source="deep",
                    confidence=0.95
                )
            )

    db.commit()
    db.close()

    print("========== EXPERTISE COMPUTATION COMPLETE ==========")