"""Embedder service using sentence-transformers.

Provides batch embedding with optional async wrapper.
"""
from __future__ import annotations

import os
import logging
import asyncio
from typing import List, Iterable, Optional

from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None) -> None:
        model_name = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self._model_name = model_name
        logger.info("Loading embedding model %s", model_name)
        # SentenceTransformer chooses device automatically; pass device via env var if needed
        self._model = SentenceTransformer(model_name)

    def embed_texts(self, texts: Iterable[str], batch_size: int = 64) -> List[List[float]]:
        """Compute embeddings for iterable of texts. Returns list of float vectors.

        This is synchronous to keep compatibility with many batch jobs. Use embed_texts_async for async usage.
        """
        texts = list(texts)
        if not texts:
            return []
        embeddings = self._model.encode(texts, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)
        # Normalize vectors to unit length for cosine similarity in Qdrant
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings = embeddings / norms
        return embeddings.tolist()

    async def embed_texts_async(self, texts: Iterable[str], batch_size: int = 64) -> List[List[float]]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.embed_texts(texts, batch_size=batch_size))


__all__ = ["Embedder"]
