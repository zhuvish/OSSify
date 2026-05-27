from collections import defaultdict
import math

from backend.app.db.postgres import SessionLocal
from backend.app.models.repository import Repository
from backend.app.models.contributor import Contributor
from backend.app.models.commit import Commit
from backend.app.models.commit_file import CommitFile
from backend.app.models.contributor_expertise import ContributorExpertise
from backend.app.models.issue import Issue
from backend.app.models.pull_request import PullRequest

from rag_pipeline.retrieval.retriever import Retriever


def get_contributor_context(db, contributor_id):
    contributor = db.query(Contributor).filter(
        Contributor.id == contributor_id
    ).first()

    if not contributor:
        return None

    expertise_rows = db.query(ContributorExpertise).filter(
        ContributorExpertise.contributor_id == contributor_id
    ).all()

    expertise = [
        {
            "domain": row.domain,
            "score": row.score
        }
        for row in expertise_rows
    ]

    commits = db.query(Commit).filter(
        Commit.contributor_id == contributor_id
    ).all()

    commit_ids = [c.id for c in commits]

    files = []

    if commit_ids:
        file_rows = db.query(CommitFile).filter(
            CommitFile.commit_id.in_(commit_ids)
        ).all()

        files = list({
            f.filename for f in file_rows
            if f.filename
        })

    return {
        "id": contributor.id,
        "username": contributor.username,
        "contributions_count": contributor.contributions_count or 0,
        "expertise": expertise,
        "files": files
    }


def compute_hybrid_score(docs, context, query):
    semantic_score = sum(
        doc["score"]
        for doc in docs
    )

    expertise_score = 0

    if context["expertise"]:
        expertise_score = max(
            row["score"]
            for row in context["expertise"]
        ) / 100

    activity_score = math.log1p(
        context["contributions_count"]
    ) / 10

    query_lower = query.lower()

    file_bonus = 0

    for filename in context["files"]:
        if any(
            token in filename.lower()
            for token in query_lower.split()
        ):
            file_bonus += 0.2

    final_score = (
        0.5 * semantic_score +
        0.3 * expertise_score +
        0.10 * activity_score +
        0.15 * file_bonus
    )

    return round(final_score, 4)


# def find_experts(query):
#     retriever = Retriever()
#     results = retriever.search(query, top_k=50)
#     db = SessionLocal()

#     try:
#         contributor_scores = defaultdict(float)
#         contributor_evidence = defaultdict(list)

#         weights = {
#             "commit": 1.5,
#             "pr": 1.1,
#             "issue": 0.8
#         }

#         for r in results:
#             payload = r["payload"]
#             cid = payload.get("contributor_id")

#             if not cid:
#                 continue

#             doc_type = payload.get("document_type")
#             score = r["score"] * weights.get(doc_type, 1.0)

#             contributor_scores[cid] += score
#             contributor_evidence[cid].append(payload)

#         ranked = sorted(
#             contributor_scores.items(),
#             key=lambda x: x[1],
#             reverse=True
#         )

#         output = []

#         for contributor_id, score in ranked[:5]:
#             contributor = db.query(Contributor).filter_by(
#                 id=contributor_id
#             ).first()

#             expertise = db.query(ContributorExpertise).filter_by(
#                 contributor_id=contributor_id,
#                 source="deep"
#             ).order_by(
#                 ContributorExpertise.score.desc()
#             ).first()

#             output.append({
#                 "username": contributor.username if contributor else "unknown",
#                 "score": round(score, 3),
#                 "expertise": expertise.domain if expertise else None
#             })

#         return output
    
#     finally:
#         db.close()


def find_experts(query, top_k=5):
    retriever = Retriever()
    results = retriever.search(query, top_k=50)
    db = SessionLocal()

    try:
        contributor_scores = defaultdict(float)
        contributor_evidence = defaultdict(list)

        weights = {
            "commit": 1.5,
            "pr": 1.1,
            "issue": 0.8
        }

        for r in results:
            payload = r["payload"]
            cid = payload.get("contributor_id")

            if not cid:
                continue

            doc_type = payload.get("document_type")
            score = r["score"] * weights.get(doc_type, 1.0)

            if doc_type == "commit":
                commit_sha = payload.get("commit_sha")

                if commit_sha:
                    commit = db.query(Commit).filter_by(
                        sha=commit_sha
                    ).first()

                    if commit:
                        file_rows = db.query(CommitFile).filter_by(
                            commit_id=commit.id
                        ).all()

                        query_tokens = query.lower().split()

                        matched = any(
                            f.filename and any(
                                token in f.filename.lower()
                                for token in query_tokens
                            )
                            for f in file_rows
                        )

                        if matched:
                            score += 0.8

            contributor_scores[cid] += score
            contributor_evidence[cid].append(r)

        ranked = sorted(
            contributor_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        output = []

        for contributor_id, score in ranked[:top_k]:
            contributor = db.query(Contributor).filter_by(
                id=contributor_id
            ).first()

            if not contributor:
                continue

            expertise = db.query(ContributorExpertise).filter_by(
                contributor_id=contributor_id,
                source="deep"
            ).order_by(
                ContributorExpertise.score.desc()
            ).first()

            commits = db.query(Commit).filter_by(
                contributor_id=contributor_id
            ).all()

            commit_ids = [c.id for c in commits]

            matched_files = []

            if commit_ids:
                file_rows = db.query(CommitFile).filter(
                    CommitFile.commit_id.in_(commit_ids)
                ).all()

                query_tokens = query.lower().split()

                matched_files = list({
                    f.filename
                    for f in file_rows
                    if f.filename and any(
                        token in f.filename.lower()
                        for token in query_tokens
                    )
                })

            evidence = contributor_evidence[contributor_id]

            output.append({
                "username": contributor.username,
                "score": round(score, 3),
                "expertise": expertise.domain if expertise else None,
                "matched_documents": len(evidence),
                "matched_files": matched_files[:5],
                "confidence": round(
                    min(score / 5, 0.95),
                    2
                )
            })

        return output

    finally:
        db.close()