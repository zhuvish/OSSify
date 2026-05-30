"""Contributor-grounded retrieval and expert discovery services.

Reuses Retriever and QdrantVectorStore for metadata-filtered semantic search.
All retrieval uses LOCAL PostgreSQL contributor IDs (not GitHub IDs).
"""
from __future__ import annotations

import logging
import math
import os
import re
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
      1. Semantic search across all Qdrant documents (top_k=100 raw for better recall)
      2. Aggregate scores per contributor with document-type weighting
      3. Apply content-token matching bonus for documents whose content contains query terms
      4. Enrich from PostgreSQL: expertise areas, matched files, stats
      5. Rank and return top-k experts

    Scoring weights:
      - commit:  1.5
      - pr:      1.2
      - issue:   0.8
      + content keyword match bonus: 0.3 per matched keyword occurrence
      + file-path token match bonus: 0.5 per matched file (max 2.0)
    """
    retriever = Retriever()
    # Increase raw recall for better expert discovery
    results = retriever.search(query, top_k=100)
    db = SessionLocal()

    try:
        # ── aggregate raw scores per contributor ──
        contrib_scores: Dict[int, float] = defaultdict(float)
        contrib_evidence: Dict[int, List[Dict]] = defaultdict(list)
        contrib_file_tokens: Dict[int, set] = defaultdict(set)
        contrib_doc_types: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        weights = {"commit": 1.5, "pr": 1.2, "issue": 0.8}
        # Extract meaningful tokens from query - split on non-alphanumeric and filter short words
        query_tokens = set()
        for raw_token in re.split(r'[^a-zA-Z0-9_#.]+', query.lower()):
            token = raw_token.strip()
            if len(token) > 2:  # ignore very short tokens
                query_tokens.add(token)

        for r in results:
            payload = r.get("payload", {})
            cid = payload.get("contributor_id")
            if not cid:
                continue

            doc_type = payload.get("document_type", "")
            score = r.get("score", 0.0) * weights.get(doc_type, 1.0)
            content = (payload.get("content") or r.get("content") or "").lower()

            # ── Content keyword match bonus ──
            # Count how many query tokens appear in the document content
            keyword_matches = 0
            for token in query_tokens:
                if token in content:
                    keyword_matches += 1
            content_bonus = min(keyword_matches * 0.3, 1.5)
            score += content_bonus

            # ── File-path token bonus from changed_files payload ──
            changed_files = (payload.get("changed_files") or "")
            for fname in changed_files.split(","):
                fname = fname.strip().lower()
                if not fname:
                    continue
                # Check if any query token matches parts of the filename
                fname_parts = set(re.split(r'[/_\-\.]', fname))
                if query_tokens & fname_parts:
                    contrib_file_tokens[cid].add(fname)

            # ── Track document types for diversity bonus ──
            contrib_doc_types[cid][doc_type] += 1

            contrib_scores[cid] += score
            contrib_evidence[cid].append(r)

        # ── File-path bonus (cap at 2.0) ──
        for cid in contrib_scores:
            bonus = min(len(contrib_file_tokens.get(cid, set())) * 0.5, 2.0)
            contrib_scores[cid] += bonus

        # ── Diversity bonus: contributors with multiple document types get a boost ──
        for cid in contrib_scores:
            type_count = len(contrib_doc_types.get(cid, {}))
            if type_count >= 2:
                contrib_scores[cid] *= (1.0 + (type_count - 1) * 0.1)

        # ── Domain-aware boosting: detect if query asks about a known domain and boost matching expertise ──
        known_domains = {"backend", "frontend", "testing", "documentation", "devops", "database"}
        query_lc = query.lower()
        found_domains = {d for d in known_domains if d in query_lc}
        if found_domains and contrib_scores:
            # Only consider contributors we already scored to avoid scanning the whole DB
            try:
                matching_expertise = (
                    db.query(ContributorExpertise)
                    .filter(ContributorExpertise.contributor_id.in_(list(contrib_scores.keys())))
                    .filter(ContributorExpertise.domain.in_(list(found_domains)))
                    .all()
                )
                # Additive boost proportional to the contributor's expertise score for the domain
                DOMAIN_BOOST_FACTOR = 0.05
                for ex in matching_expertise:
                    contrib_scores[ex.contributor_id] += ex.score * DOMAIN_BOOST_FACTOR
            except Exception:
                # Avoid failing the whole search if DB lookup misbehaves
                logger.exception("Domain boosting failed")

        # ── rank contributors by aggregated score ──
        ranked = sorted(contrib_scores.items(), key=lambda kv: kv[1], reverse=True)

        # ── build output (skip bot accounts and include top evidence) ──
        output: List[Dict[str, Any]] = []
        added = 0
        for contributor_id, score in ranked:
            if added >= top_k:
                break

            contributor = db.query(Contributor).filter_by(id=contributor_id).first()
            if not contributor:
                continue

            # Exclude bot accounts (username contains "bot", case-insensitive)
            if contributor.username and "bot" in contributor.username.lower():
                continue

            # expertise areas: aggregate duplicate domains from ContributorExpertise
            expertise_rows = (
                db.query(ContributorExpertise)
                .filter_by(contributor_id=contributor_id)
                .all()
            )
            expertise_map: Dict[str, Dict[str, Any]] = {}
            for row in expertise_rows:
                dom = (row.domain or "").lower()
                if not dom:
                    continue
                if dom not in expertise_map:
                    expertise_map[dom] = {
                        "domain": row.domain,
                        "score": float(row.score or 0.0),
                        "evidence_count": int(row.evidence_count or 0),
                        "confidence": float(row.confidence or 0.0),
                    }
                else:
                    # Aggregate scores and evidence counts; average confidence weighted by score
                    expertise_map[dom]["score"] += float(row.score or 0.0)
                    expertise_map[dom]["evidence_count"] += int(row.evidence_count or 0)
                    # weighted avg confidence
                    existing_conf = expertise_map[dom]["confidence"]
                    new_conf = float(row.confidence or 0.0)
                    total = expertise_map[dom]["score"]
                    # avoid divide by zero
                    if total > 0:
                        expertise_map[dom]["confidence"] = (existing_conf + new_conf) / 2.0

            expertise_areas = sorted(
                [
                    {
                        "domain": v["domain"],
                        "score": round(v["score"], 3),
                        "evidence_count": v["evidence_count"],
                        "confidence": round(min(v["confidence"], 0.99), 3),
                    }
                    for v in expertise_map.values()
                ],
                key=lambda x: x["score"],
                reverse=True,
            )

            # top expertise domain
            top_expertise = expertise_areas[0]["domain"] if expertise_areas else None

            # matched files from evidence
            matched_files = sorted(contrib_file_tokens.get(contributor_id, set()))[:5]

            # evidence count = unique matched documents
            evidence_count = len(contrib_evidence[contributor_id])

            # top evidence documents (up to 3), sorted by score
            top_docs = sorted(contrib_evidence[contributor_id], key=lambda d: d.get("score", 0), reverse=True)[:3]
            top_evidence = []
            for d in top_docs:
                payload = d.get("payload", {})
                top_evidence.append({
                    "document_type": payload.get("document_type"),
                    "score": d.get("score", 0),
                    "commit_sha": payload.get("commit_sha"),
                    "pr_number": payload.get("pr_number"),
                    "issue_number": payload.get("issue_number"),
                })

            # confidence: normalized against a softer scale, cap at 0.95
            confidence = round(min(score / 8.0, 0.95), 2)

            output.append({
                "contributor_id": contributor.id,
                "username": contributor.username,
                "score": round(score, 3),
                "expertise": top_expertise,
                "expertise_areas": expertise_areas,
                "matched_documents": evidence_count,
                "matched_files": matched_files,
                "confidence": confidence,
                "top_evidence": top_evidence,
            })

            added += 1

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
            .filter_by(
                contributor_id=contributor_id,
                source="deep"
            )
            .all()
        )
        # Aggregate duplicate domains (across sources) into single entries
        expertise_map: Dict[str, Dict[str, Any]] = {}
        for row in expertise_rows:
            dom = (row.domain or "").lower()
            if not dom:
                continue
            if dom not in expertise_map:
                expertise_map[dom] = {
                    "domain": row.domain,
                    "score": float(row.score or 0.0),
                    "evidence_count": int(row.evidence_count or 0),
                    "confidence": float(row.confidence or 0.0),
                }
            else:
                expertise_map[dom]["score"] += float(row.score or 0.0)
                expertise_map[dom]["evidence_count"] += int(row.evidence_count or 0)
                # simple average of confidences
                expertise_map[dom]["confidence"] = (
                    expertise_map[dom]["confidence"] + float(row.confidence or 0.0)
                ) / 2.0

        expertise_areas = sorted(
            [
                {
                    "domain": v["domain"],
                    "score": round(v["score"], 3),
                    "evidence_count": v["evidence_count"],
                    "confidence": round(min(v["confidence"], 0.99), 3),
                }
                for v in expertise_map.values()
            ],
            key=lambda x: x["score"],
            reverse=True,
        )

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
            # Use the content that was already resolved by QdrantVectorStore with fallback
            snippet = (doc.get("content") or payload.get("content") or "")[:400]
            if not snippet.strip():
                # Last resort fallback: build from payload fields
                parts = []
                doc_type = payload.get("document_type", "")
                if doc_type == "commit":
                    parts.append(f"Commit: {payload.get('commit_message', '') or payload.get('message', '')}")
                elif doc_type == "pr":
                    parts.append(f"PR: {payload.get('title', '')}")
                elif doc_type == "issue":
                    parts.append(f"Issue: {payload.get('title', '')}")
                parts.append(f"Repository: {payload.get('repo', '')}")
                snippet = " | ".join(p for p in parts if p)[:400] or "(no content available)"

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