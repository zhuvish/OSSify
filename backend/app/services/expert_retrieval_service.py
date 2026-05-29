"""Contributor-grounded retrieval and expert discovery services.

Reuses Retriever and QdrantVectorStore for metadata-filtered semantic search.
All retrieval uses LOCAL PostgreSQL contributor IDs (not GitHub IDs).
"""
from __future__ import annotations

import logging
import math
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from backend.app.db.postgres import SessionLocal
from backend.app.models.contributor import Contributor
from backend.app.models.commit import Commit
from backend.app.models.commit_file import CommitFile
from backend.app.models.contributor_expertise import ContributorExpertise
from backend.app.models.issue import Issue
from backend.app.models.pull_request import PullRequest
from backend.app.models.repository import Repository

from rag_pipeline.retrieval.retriever import Retriever

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
#  Expert Search
# ──────────────────────────────────────────────


def find_experts(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Find experts for a given query by aggregating semantically relevant documents.

    Pipeline:
      1. Semantic search across all Qdrant documents (top_k=50 raw)
      2. Aggregate scores per contributor with document-type weighting
      3. Enrich from PostgreSQL: expertise areas, matched files, stats
      4. Rank and return top-k experts

    Scoring weights:
      - commit:  1.5
      - pr:      1.2
      - issue:   0.8
      + file-path token match bonus: 0.5 per matched file (max 2.0)
    """
    retriever = Retriever()
    results = retriever.search(query, top_k=50)
    db = SessionLocal()

    try:
        # ── aggregate raw scores per contributor ──
        contrib_scores: Dict[int, float] = defaultdict(float)
        contrib_evidence: Dict[int, List[Dict]] = defaultdict(list)
        contrib_file_tokens: Dict[int, set] = defaultdict(set)

        weights = {"commit": 1.5, "pr": 1.2, "issue": 0.8}
        query_tokens = set(query.lower().split())

        for r in results:
            payload = r.get("payload", {})
            cid = payload.get("contributor_id")
            if not cid:
                continue

            doc_type = payload.get("document_type", "")
            score = r.get("score", 0.0) * weights.get(doc_type, 1.0)

            # file-path token bonus from changed_files payload if available
            changed_files = (payload.get("changed_files") or "")
            for fname in changed_files.split(","):
                fname = fname.strip().lower()
                if not fname:
                    continue
                if query_tokens & set(fname.replace("/", " ").replace("_", " ").replace("-", " ").split()):
                    contrib_file_tokens[cid].add(fname)

            contrib_scores[cid] += score
            contrib_evidence[cid].append(r)

        # add file-path bonus (cap at 2.0)
        for cid in contrib_scores:
            bonus = min(len(contrib_file_tokens.get(cid, set())) * 0.5, 2.0)
            contrib_scores[cid] += bonus

        # ── rank ──
        ranked = sorted(contrib_scores.items(), key=lambda kv: kv[1], reverse=True)

        # ── build output ──
        output: List[Dict[str, Any]] = []
        for contributor_id, score in ranked[:top_k]:
            contributor = db.query(Contributor).filter_by(id=contributor_id).first()
            if not contributor:
                continue

            # expertise areas
            expertise_rows = (
                db.query(ContributorExpertise)
                .filter_by(contributor_id=contributor_id)
                .order_by(ContributorExpertise.score.desc())
                .all()
            )
            expertise_areas = [
                {"domain": row.domain, "score": row.score}
                for row in expertise_rows
            ]

            # top expertise domain
            top_expertise = expertise_areas[0]["domain"] if expertise_areas else None

            # matched files from evidence
            matched_files = sorted(contrib_file_tokens.get(contributor_id, set()))[:5]

            # evidence count = unique matched documents
            evidence_count = len(contrib_evidence[contributor_id])

            # confidence: normalized score capped at 0.95
            confidence = round(min(score / 5.0, 0.95), 2)

            output.append({
                "contributor_id": contributor.id,
                "username": contributor.username,
                "score": round(score, 3),
                "expertise": top_expertise,
                "expertise_areas": expertise_areas,
                "matched_documents": evidence_count,
                "matched_files": matched_files,
                "confidence": confidence,
            })

        return output

    finally:
        db.close()


# ──────────────────────────────────────────────
#  Contributor Profile
# ──────────────────────────────────────────────


def get_contributor_profile(contributor_id: int) -> Optional[Dict[str, Any]]:
    """Return a rich contributor profile combining PostgreSQL + Qdrant data.

    Returns None if contributor does not exist.
    """
    db = SessionLocal()
    try:
        contributor = db.query(Contributor).filter(Contributor.id == contributor_id).first()
        if not contributor:
            return None

        # ── expertise ──
        expertise_rows = (
            db.query(ContributorExpertise)
            .filter_by(contributor_id=contributor_id)
            .order_by(ContributorExpertise.score.desc())
            .all()
        )
        expertise_areas = [
            {
                "domain": row.domain,
                "score": row.score,
                "evidence_count": row.evidence_count,
                "confidence": row.confidence,
            }
            for row in expertise_rows
        ]

        # ── counts ──
        commit_count = db.query(Commit).filter_by(contributor_id=contributor_id).count()
        pr_count = db.query(PullRequest).filter_by(user_id=contributor_id).count()
        issue_count = db.query(Issue).filter_by(user_id=contributor_id).count()

        # ── repositories ──
        repo_ids = set()
        for c in db.query(Commit).filter_by(contributor_id=contributor_id).with_entities(Commit.repo_id).all():
            repo_ids.add(c.repo_id)
        for pr in db.query(PullRequest).filter_by(user_id=contributor_id).with_entities(PullRequest.repo_id).all():
            repo_ids.add(pr.repo_id)
        for iss in db.query(Issue).filter_by(user_id=contributor_id).with_entities(Issue.repo_id).all():
            repo_ids.add(iss.repo_id)

        repos = (
            db.query(Repository).filter(Repository.id.in_(repo_ids)).all()
            if repo_ids
            else []
        )
        top_repos = [
            {"name": r.full_name, "stars": r.stars or 0} for r in repos
        ]

        # ── top files ──
        commit_ids = [
            c.id for c in db.query(Commit).filter_by(contributor_id=contributor_id).with_entities(Commit.id).all()
        ]
        file_rows = []
        if commit_ids:
            file_rows = (
                db.query(CommitFile.filename)
                .filter(CommitFile.commit_id.in_(commit_ids))
                .all()
            )
        file_counter: Dict[str, int] = defaultdict(int)
        for (fname,) in file_rows:
            if fname:
                file_counter[fname] += 1
        top_files = sorted(file_counter, key=file_counter.get, reverse=True)[:10]

        # ── recent activity (last 10 items) ──
        recent: List[Dict[str, Any]] = []

        for c in (
            db.query(Commit)
            .filter_by(contributor_id=contributor_id)
            .order_by(Commit.date.desc())
            .limit(5)
            .all()
        ):
            recent.append({
                "type": "commit",
                "description": (c.message or "")[:120],
                "date": str(c.date) if c.date else None,
                "sha": c.sha,
                "repo_id": c.repo_id,
            })

        for pr in (
            db.query(PullRequest)
            .filter_by(user_id=contributor_id)
            .order_by(PullRequest.created_at.desc())
            .limit(5)
            .all()
        ):
            recent.append({
                "type": "pr",
                "description": (pr.title or "")[:120],
                "date": str(pr.created_at) if pr.created_at else None,
                "pr_number": pr.pr_number,
                "repo_id": pr.repo_id,
            })

        for issue in (
            db.query(Issue)
            .filter_by(user_id=contributor_id)
            .order_by(Issue.created_at.desc())
            .limit(5)
            .all()
        ):
            recent.append({
                "type": "issue",
                "description": (issue.title or "")[:120],
                "date": str(issue.created_at) if issue.created_at else None,
                "issue_number": issue.issue_number,
                "repo_id": issue.repo_id,
            })

        recent.sort(key=lambda x: x["date"] or "", reverse=True)
        recent = recent[:10]

        # ── semantic expertise summary from Qdrant ──
        semantic_summary = _build_semantic_expertise_summary(contributor_id)

        return {
            "contributor_id": contributor.id,
            "username": contributor.username,
            "avatar_url": contributor.avatar_url,
            "profile_url": contributor.profile_url,
            "display_name": contributor.display_name,
            "bio": contributor.bio,
            "company": contributor.company,
            "location": contributor.location,
            "followers": contributor.followers,
            "contributions_count": contributor.contributions_count,
            "expertise_areas": expertise_areas,
            "top_repositories": top_repos,
            "top_files": top_files,
            "commit_count": commit_count,
            "pr_count": pr_count,
            "issue_count": issue_count,
            "recent_activity": recent,
            "semantic_expertise_summary": semantic_summary,
        }

    finally:
        db.close()


def _build_semantic_expertise_summary(contributor_id: int) -> List[Dict[str, Any]]:
    """Use Qdrant semantic search to discover top expertise domains for a contributor."""
    from rag_pipeline.retrieval.retriever import Retriever

    retriever = Retriever()

    # Search across contributor's docs with broad queries to find thematic clusters
    broad_queries = [
        "architecture design pattern",
        "bug fix error handling",
        "feature implementation",
        "testing deployment",
        "documentation refactor",
    ]

    discovered: Dict[str, float] = defaultdict(float)
    for q in broad_queries:
        docs = retriever.search_by_contributor(query=q, contributor_id=contributor_id, top_k=5)
        for doc in docs:
            content = (doc.get("payload") or {}).get("content", "")[:500]
            # simple keyword extraction from content
            for token in content.lower().split():
                if len(token) > 4 and token not in {"repository", "contributor", "commit", "message", "changed", "files"}:
                    discovered[token] += doc.get("score", 0) * 0.1

    # return top discovered keywords as summary
    sorted_keywords = sorted(discovered.items(), key=lambda kv: kv[1], reverse=True)
    return [
        {"term": term, "relevance": round(score, 3)}
        for term, score in sorted_keywords[:8]
    ]


# ──────────────────────────────────────────────
#  Contributor-Grounded RAG (Digital Twin)
# ──────────────────────────────────────────────


def answer_for_contributor(
    contributor_id: int,
    question: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    """Answer a question using ONLY documents from the specified contributor.

    This is the **digital twin** endpoint — retrieval is strictly scoped
    to the contributor's own commits / PRs / issues.
    Never mixes documents from other contributors.

    Returns a dict with:
      - answer              (str, LLM-generated or placeholder)
      - evidence            (list of matched docs with snippets)
      - contributor_id      (int)
      - username            (str)
      - grounding_status    ("contributor_scoped" | "no_matches")
      - document_count      (int)
    """
    db = SessionLocal()
    try:
        contributor = db.query(Contributor).filter(Contributor.id == contributor_id).first()
        if not contributor:
            return {"error": f"Contributor with ID {contributor_id} not found"}

        retriever = Retriever()
        results = retriever.search_by_contributor(
            query=question,
            contributor_id=contributor_id,
            top_k=top_k,
        )

        if not results:
            return {
                "contributor_id": contributor_id,
                "username": contributor.username,
                "answer": "No relevant documents found for this contributor.",
                "evidence": [],
                "grounding_status": "no_matches",
                "document_count": 0,
            }

        # ── build evidence ──
        evidence = []
        context_blocks = []
        for i, doc in enumerate(results, 1):
            payload = doc.get("payload", {})
            snippet = (payload.get("content") or "")[:400]
            context_blocks.append(
                f"[Document {i}] Type: {payload.get('document_type')} | "
                f"Score: {doc.get('score', 0):.4f}\n{snippet}"
            )
            evidence.append({
                "document_type": payload.get("document_type"),
                "content_snippet": snippet,
                "score": doc.get("score", 0),
                "commit_sha": payload.get("commit_sha"),
                "pr_number": payload.get("pr_number"),
                "issue_number": payload.get("issue_number"),
            })

        context = "\n\n".join(context_blocks)
        answer = _generate_answer(question, context, contributor.username)

        return {
            "contributor_id": contributor_id,
            "username": contributor.username,
            "question": question,
            "answer": answer,
            "evidence": evidence,
            "grounding_status": "contributor_scoped",
            "document_count": len(results),
        }

    finally:
        db.close()


def _generate_answer(question: str, context: str, username: str) -> str:
    """Generate an LLM answer grounded in the provided context."""
    if not os.getenv("GROQ_API_KEY"):
        return "LLM not configured – see evidence for retrieved documents."

    try:
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""You are answering a question about a software contributor's work.

RULES:
1. Answer ONLY from the provided context (commits, PRs, issues).
2. Do NOT use general knowledge.
3. If context is insufficient, say so clearly.

Contributor: {username}
Question: {question}

Context from {username}'s work:
{context}

Answer:"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.exception("LLM call failed")
        return f"Error generating answer: {e}"