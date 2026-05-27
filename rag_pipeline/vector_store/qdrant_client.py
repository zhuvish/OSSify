"""
Qdrant client wrapper for contributor-centric vector store.
Provides: create_collection, upsert_points, semantic_search, filtered search helpers.
"""
from __future__ import annotations

import os
import logging
import time
from typing import Any, Dict, Iterable, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as q_models

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Wrapper around qdrant-client for contributor-centric documents.

    Uses payloads to store contributor, repo, document_type, file_paths, module, timestamps, and references.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        default_collection: str = "contributors",
    ) -> None:
        url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        api_key = api_key or os.getenv("QDRANT_API_KEY")
        self._client = QdrantClient(url=url, api_key=api_key)
        self.collection = default_collection

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: q_models.Distance = q_models.Distance.COSINE,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        params = q_models.VectorParams(size=vector_size, distance=distance)
        try:
            if collection_name in [c.name for c in self._client.get_collections().collections]:
                logger.info("Collection '%s' already exists", collection_name)
                self.collection = collection_name
                return
        except Exception:
            # ignore if get_collections fails (older qdrant versions) and attempt create
            pass

        logger.info("Creating collection %s (size=%s distance=%s)", collection_name, vector_size, distance)
        self._client.recreate_collection(
            collection_name=collection_name,
            vectors_config=q_models.VectorParams(size=vector_size, distance=distance),
        )
        if metadata:
            try:
                self._client.update_collection(collection_name=collection_name, params={"config": metadata})
            except Exception:
                logger.debug("Could not attach metadata to collection %s", collection_name)
        self.collection = collection_name

    def upsert_points(self, points: Iterable[Dict[str, Any]], batch_size: int = 256) -> None:
        """Upsert points into the current collection.

        Each point must be dict with keys: 'id' (str|int), 'vector' (List[float]), 'payload' (dict)
        """
        buf: List[q_models.PointStruct] = []
        for p in points:
            pt = q_models.PointStruct(id=p["id"], vector=p["vector"], payload=p.get("payload"))
            buf.append(pt)
            if len(buf) >= batch_size:
                self._upsert_batch(buf)
                buf = []
        if buf:
            self._upsert_batch(buf)

    def _upsert_batch(self, batch: List[q_models.PointStruct]) -> None:
        for attempt in range(3):
            try:
                self._client.upsert(collection_name=self.collection, points=batch)
                return
            except Exception as exc:
                logger.warning("Upsert attempt %d failed: %s", attempt + 1, exc)
                time.sleep(1 + attempt * 2)
        raise RuntimeError("Failed to upsert points to qdrant after retries")

    def semantic_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter: Optional[q_models.Filter] = None,
        with_payload: bool = True,
    ) -> List[Dict[str, Any]]:
        """Perform semantic search returning point id, score, and payload.
        """
        try:
            results = self._client.query_points(
                collection_name=self.collection,
                query=query_vector,
                limit=top_k,
                query_filter=filter,
                with_payload=with_payload,
            )
        except Exception as exc:
            logger.exception("Qdrant search failed: %s", exc)
            return []

        out = []
        for p in results.points:
            out.append({
                "id": p.id, 
                "score": p.score, 
                "payload": p.payload,
                "content": p.payload.get("content", "")
            })
        return out

    def build_filter_for_contributor(self, contributor_login: str) -> q_models.Filter:
        return q_models.Filter(must=[q_models.FieldCondition(key="contributor", match=q_models.MatchValue(value=contributor_login))])

    def build_filter(self, **kwargs) -> q_models.Filter:
        """Build a composite filter from kwargs (repo, contributor, document_type).

        Values are matched exactly.
        """
        must_conditions: List[q_models.FieldCondition] = []
        for k, v in kwargs.items():
            if v is None:
                continue
            must_conditions.append(q_models.FieldCondition(key=k, match=q_models.MatchValue(value=v)))
        if not must_conditions:
            return q_models.Filter()
        return q_models.Filter(must=must_conditions)

    def count_points(self) -> int:
        try:
            stats = self._client.get_collection(collection_name=self.collection).result
            return stats.vectors.count if stats and stats.vectors else 0
        except Exception:
            # Fallback
            info = self._client.get_collection(collection_name=self.collection)
            return getattr(info, "points_count", 0)

    def delete_collection(self, collection_name: Optional[str] = None) -> None:
        cname = collection_name or self.collection
        self._client.delete_collection(collection_name=cname)


__all__ = ["QdrantVectorStore"]
