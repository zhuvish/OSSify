from collections import defaultdict

from backend.app.db.postgres import SessionLocal

from backend.app.models.contributor import Contributor
from backend.app.models.commit import Commit
from backend.app.models.commit_file import CommitFile
from backend.app.models.contributor_expertise import ContributorExpertise

from backend.app.services.expertise_classifier import classify_file


def compute_expertise():
    db = SessionLocal()

    print("\n========== STARTING EXPERTISE COMPUTATION ==========")

    db.query(ContributorExpertise).delete()
    db.commit()

    contributors = db.query(Contributor).all()

    for contributor in contributors:
        print(f"Analyzing contributor: {contributor.username}")

        domain_scores = defaultdict(int)

        commits = db.query(Commit).filter_by(
            contributor_id=contributor.id
        ).all()

        if not commits:
            continue

        for commit in commits:
            files = db.query(CommitFile).filter_by(
                commit_id=commit.id
            ).all()

            for file in files:
                domains = classify_file(file.filename)

                for domain in domains:
                    weight = file.changes if file.changes else 1
                    domain_scores[domain] += weight

        if not domain_scores:
            continue

        max_score = max(domain_scores.values())

        for domain, raw_score in domain_scores.items():
            normalized_score = round(
                (raw_score / max_score) * 100,
                2
            )

            expertise = ContributorExpertise(
                contributor_id=contributor.id,
                domain=domain,
                score=normalized_score,
                evidence_count=raw_score
            )

            db.add(expertise)

    db.commit()
    db.close()

    print("========== EXPERTISE COMPUTATION COMPLETE ==========")