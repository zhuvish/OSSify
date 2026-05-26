from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid


class DocumentMetadata(BaseModel):
    # preserve DB numeric ids for backwards compatibility
    repo_id: Optional[int] = None
    contributor_db_id: Optional[int] = None

    # human-friendly fields for Qdrant payloads
    repo: Optional[str] = None
    contributor: Optional[str] = None
    # contributor_id is the GitHub account id (string or int as provided by GitHub)
    contributor_id: Optional[str] = None

    document_type: str
    timestamp: Optional[datetime] = None
    commit_sha: Optional[str] = None
    pr_number: Optional[int] = None
    issue_number: Optional[int] = None


class ContributorDocument(BaseModel):
    id: str
    content: str
    metadata: DocumentMetadata


class DocumentBuilder:

    @staticmethod
    def _make_id(prefix: str, source_id: Any) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{prefix}:{source_id}"))

    @staticmethod
    def _normalize_timestamp(ts):
        if ts is None:
            return None

        if isinstance(ts, datetime):
            return ts

        try:
            return datetime.fromisoformat(str(ts))
        except Exception:
            return None

    @classmethod
    def from_commit_row(cls, row: Dict[str, Any]):

        # row is expected to contain: repo (full_name), contributor (username), contributor_id (github id)
        metadata = DocumentMetadata(
            repo_id=row.get("repo_id"),
            contributor_db_id=row.get("contributor_db_id"),
            repo=row.get("repo"),
            contributor=row.get("contributor"),
            contributor_id=str(row.get("contributor_id")) if row.get("contributor_id") is not None else None,
            document_type="commit",
            timestamp=cls._normalize_timestamp(row.get("date")),
            commit_sha=row.get("sha"),
        )

        content = row.get("message") or ""

        doc_id = cls._make_id(
            "commit",
            row.get("sha") or row.get("id")
        )

        return ContributorDocument(
            id=doc_id,
            content=content,
            metadata=metadata
        )

    @classmethod
    def from_pr_row(cls, row: Dict[str, Any]):

        metadata = DocumentMetadata(
            repo_id=row.get("repo_id"),
            contributor_db_id=row.get("contributor_db_id"),
            repo=row.get("repo"),
            contributor=row.get("contributor"),
            contributor_id=str(row.get("contributor_id")) if row.get("contributor_id") is not None else None,
            document_type="pr",
            timestamp=cls._normalize_timestamp(row.get("created_at")),
            pr_number=row.get("pr_number"),
        )

        title = row.get("title") or ""
        body = row.get("body") or ""

        content = f"{title}\n\n{body}".strip()

        doc_id = cls._make_id(
            "pr",
            row.get("id")
        )

        return ContributorDocument(
            id=doc_id,
            content=content,
            metadata=metadata
        )

    @classmethod
    def from_issue_row(cls, row: Dict[str, Any]):

        metadata = DocumentMetadata(
            repo_id=row.get("repo_id"),
            repo=row.get("repo"),
            document_type="issue",
            timestamp=cls._normalize_timestamp(row.get("created_at")),
            issue_number=row.get("issue_number"),
        )

        title = row.get("title") or ""
        body = row.get("body") or ""

        content = f"{title}\n\n{body}".strip()

        doc_id = cls._make_id(
            "issue",
            row.get("id")
        )

        return ContributorDocument(
            id=doc_id,
            content=content,
            metadata=metadata
        )