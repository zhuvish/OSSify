from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid


class DocumentMetadata(BaseModel):
    repo_id: Optional[int] = None
    contributor_id: Optional[int] = None
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
        return str(uuid.uuid4())

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

        metadata = DocumentMetadata(
            repo_id=row.get("repo_id"),
            contributor_id=row.get("contributor_id"),
            document_type="commit",
            timestamp=cls._normalize_timestamp(row.get("date")),
            commit_sha=row.get("sha"),
        )

        message = row.get("message") or ""
        repo = row.get("repo") or ""
        contributor = row.get("contributor") or ""
        changed_files = row.get("changed_files") or ""

        content = f"""
            Commit message: {message}
            Repository: {repo}
            Contributor: {contributor}
            Changed files: {changed_files}
        """.strip()

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
            contributor_id=row.get("contributor_id"),
            document_type="pr",
            timestamp=cls._normalize_timestamp(row.get("created_at")),
            pr_number=row.get("pr_number"),
        )

        title = row.get("title") or ""
        body = row.get("body") or ""
        repo = row.get("repo") or ""
        contributor = row.get("contributor") or ""

        content = f"""
            Pull Request: {title}

            Description: {body}

            Repository: {repo}
            Contributor: {contributor}
        """.strip()

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
            contributor_id=row.get("contributor_id"),
            document_type="issue",
            timestamp=cls._normalize_timestamp(row.get("created_at")),
            issue_number=row.get("issue_number"),
        )

        title = row.get("title") or ""
        body = row.get("body") or ""
        repo = row.get("repo") or ""
        contributor = row.get("contributor") or ""

        content = f"""
            Issue: {title}

            Description: {body}

            Repository: {repo}
            Contributor: {contributor}
        """.strip()

        doc_id = cls._make_id(
            "issue",
            row.get("id")
        )

        return ContributorDocument(
            id=doc_id,
            content=content,
            metadata=metadata
        )