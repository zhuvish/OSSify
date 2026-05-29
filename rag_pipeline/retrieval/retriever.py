from typing import Any, Dict, List, Optional

from rag_pipeline.embeddings.embedder import Embedder
from rag_pipeline.vector_store.qdrant_client import QdrantVectorStore


class Retriever:
    """Semantic retriever with optional metadata filtering for contributor-grounded RAG."""

    def __init__(self, collection: str = "repo_documents"):
        self.embedder = Embedder()
        self.vector_store = QdrantVectorStore(default_collection=collection)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Basic semantic search without filtering."""
        query_vector = self.embedder.embed_texts([query])[0]
        results = self.vector_store.semantic_search(
            query_vector=query_vector,
            top_k=top_k
        )
        return results

    def search_with_filter(
        self,
        query: str,
        top_k: int = 5,
        contributor_id: Optional[int] = None,
        repo_id: Optional[int] = None,
        document_type: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Semantic search with metadata filtering.

        Args:
            query: Search query text
            top_k: Number of results to return
            contributor_id: Filter by local PostgreSQL contributor ID
            repo_id: Filter by repository ID
            document_type: Filter by document type (commit, pr, issue)
            **kwargs: Additional filter conditions passed to build_filter

        Returns:
            List of matching documents with scores and payloads
        """
        query_vector = self.embedder.embed_texts([query])[0]

        # Build filter from provided parameters
        filter_params = {}
        if contributor_id is not None:
            filter_params["contributor_id"] = contributor_id
        if repo_id is not None:
            filter_params["repo_id"] = repo_id
        if document_type is not None:
            filter_params["document_type"] = document_type
        filter_params.update(kwargs)

        qdrant_filter = self.vector_store.build_filter(**filter_params)

        results = self.vector_store.semantic_search(
            query_vector=query_vector,
            top_k=top_k,
            filter=qdrant_filter
        )
        return results

    def search_by_contributor(
        self,
        query: str,
        contributor_id: int,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search documents belonging to a specific contributor.

        This enables contributor-grounded RAG - answering questions
        using only documents from a specific contributor's work.

        Args:
            query: Search query text
            contributor_id: Local PostgreSQL contributor ID
            top_k: Number of results to return

        Returns:
            List of matching documents with scores and payloads
        """
        return self.search_with_filter(
            query=query,
            top_k=top_k,
            contributor_id=contributor_id
        )

    def search_experts(
        self,
        query: str,
        top_k: int = 50
    ) -> List[Dict[str, Any]]:
        """Search for expert discovery - returns many results for ranking.

        Args:
            query: Search query text (e.g., "authentication", "routing")
            top_k: Number of results to return for ranking

        Returns:
            List of matching documents with scores and payloads
        """
        return self.search(query, top_k=top_k)
