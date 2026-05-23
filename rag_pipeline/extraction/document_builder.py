"""Build unified documents combining code, commits, and PR data for RAG indexing."""

from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DocumentBuilder:
    """Build searchable documents from extracted data."""

    def __init__(self):
        """Initialize document builder."""
        pass

    def build_code_document(
        self,
        file_path: str,
        content: str,
        language: str,
        module: str,
    ) -> Dict[str, Any]:
        """Build a searchable document from a code file.

        Returns a dict with id, content and metadata keys.
        """
                # Normalize file path separators to underscores for id
        doc_id = 'code_' + file_path.replace('/', '_').replace('\\', '_')
        return {
            "id": doc_id,
            "content": content,
            "metadata": {
                "type": "code",
                "file_path": file_path,
                "language": language,
                "module": module,
                "indexed_at": datetime.utcnow().isoformat() + "Z",
            },
        }

    def build_commit_document(
        self,
        commit_hash: str,
        message: str,
        author: str,
        timestamp: str,
        body: str = "",
    ) -> Dict[str, Any]:
        """Build a searchable document from a commit."""
        doc_id = f"commit_{commit_hash[:8]}"
        content = (message or "") + ("\n\n" + body if body else "")
        return {
            "id": doc_id,
            "content": content.strip(),
            "metadata": {
                "type": "commit",
                "commit_hash": commit_hash,
                "author": author,
                "timestamp": timestamp,
                "indexed_at": datetime.utcnow().isoformat() + "Z",
            },
        }

    def build_pr_document(
        self,
        pr_number: int,
        title: str,
        description: str,
        author: str,
        timestamp: str,
    ) -> Dict[str, Any]:
        """Build a searchable document from a pull request."""
        doc_id = f"pr_{pr_number}"
        content = (title or "") + ("\n\n" + description if description else "")
        return {
            "id": doc_id,
            "content": content.strip(),
            "metadata": {
                "type": "pr",
                "pr_number": pr_number,
                "author": author,
                "timestamp": timestamp,
                "indexed_at": datetime.utcnow().isoformat() + "Z",
            },
        }

    def build_issue_document(
        self,
        issue_number: int,
        title: str,
        body: str,
        author: str,
        created_at: str,
    ) -> Dict[str, Any]:
        """Build a searchable document from an issue."""
        doc_id = f"issue_{issue_number}"
        content = (title or "") + ("\n\n" + body if body else "")
        return {
            "id": doc_id,
            "content": content.strip(),
            "metadata": {
                "type": "issue",
                "issue_number": issue_number,
                "author": author,
                "created_at": created_at,
                "indexed_at": datetime.utcnow().isoformat() + "Z",
            },
        }

    def batch_build_from_code_docs(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert a list of code doc dicts (file_path/content/...) into searchable documents."""
        out = []
        for d in docs:
            out.append(self.build_code_document(
                file_path=d.get("file_path", ""),
                content=d.get("content", ""),
                language=d.get("language", "unknown"),
                module=d.get("module", "root"),
            ))
        return out

    def batch_build_from_commit_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert rows/dicts representing commits into searchable documents."""
        out = []
        for r in rows:
            out.append(self.build_commit_document(
                commit_hash=r.get("commit_hash", ""),
                message=r.get("message", ""),
                author=r.get("author", r.get("author_email", "")),
                timestamp=r.get("timestamp", ""),
                body=r.get("body", ""),
            ))
        return out

