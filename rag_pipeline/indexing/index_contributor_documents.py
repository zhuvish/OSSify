"""Index contributor-centric documents from PostgreSQL into Qdrant.

This script:
 - Connects to PostgreSQL using SQLAlchemy
 - Reads commits, pull requests, issues, and reviews
 - Builds documents with DocumentBuilder
 - Embeds content via Embedder
 - Upserts points into Qdrant via QdrantVectorStore
"""
from __future__ import annotations

import os
import logging
from typing import Iterator, List, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from rag_pipeline.documents.document_builder import DocumentBuilder
from rag_pipeline.embeddings.embedder import Embedder
from rag_pipeline.vector_store.qdrant_client import QdrantVectorStore

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

CHUNK_SIZE = int(os.getenv("INDEX_CHUNK_SIZE", "256"))
BATCH_EMBED_SIZE = int(os.getenv("BATCH_EMBED_SIZE", "128"))


def _iter_rows(engine, query: str) -> Iterator[Dict[str, Any]]:
    with engine.connect() as conn:
        try:
            rs = conn.execution_options(stream_results=True).execute(text(query))
            for row in rs:
                yield dict(row._mapping)
        except SQLAlchemyError as exc:
            logger.exception("DB query failed: %s", exc)
            return


def fetch_all_documents(engine) -> Iterator[Dict[str, Any]]:
    queries = {

    "commits": """
        SELECT
            c.id,
            c.sha,
            c.message,
            c.author_name,
            c.author_email,
            c.date,
            c.repo_id,

            c.repo_id,
            r.full_name AS repo,

            c.contributor_id AS contributor_db_id,
            ctr.username AS contributor,
            ctr.id AS contributor_id,

            STRING_AGG(cf.filename, ', ') AS changed_files

        FROM commits c

        LEFT JOIN repositories r
            ON c.repo_id = r.id

        LEFT JOIN contributors ctr
            ON c.contributor_id = ctr.id

        LEFT JOIN commit_files cf
            ON cf.commit_id = c.id

        GROUP BY
            c.id,
            c.sha,
            c.message,
            c.author_name,
            c.author_email,
            c.date,
            c.repo_id,
            r.full_name,
            ctr.username,
            ctr.id
    """,

    "prs": """
        SELECT
            pr.id,
            pr.pr_number,
            pr.title,
            pr.body,
            pr.state,
            pr.created_at,
            pr.closed_at,

            pr.repo_id,
            r.full_name AS repo,

            pr.user_id AS contributor_db_id,
            ctr.username AS contributor,
            ctr.github_id AS contributor_id

        FROM pull_requests pr

        LEFT JOIN repositories r
            ON pr.repo_id = r.id
            
        LEFT JOIN contributors ctr
            ON pr.user_id = ctr.id
    """,

    "issues": """
        SELECT
            i.id,
            i.issue_number,
            i.title,
            i.body,
            i.state,
            i.created_at,
            i.closed_at,

            i.repo_id,
            r.full_name AS repo

        FROM issues i

        LEFT JOIN repositories r
            ON i.repo_id = r.id
    """
}
    for doc_type, q in queries.items():
        for row in _iter_rows(engine, q):
            yield (doc_type, row)


def index_documents(database_url: str, qdrant_collection: str = "repo_documents") -> None:
    print("Starting indexing...")
    
    print("Connecting to PostgreSQL...")
    engine = create_engine(database_url)

    print("Loading embedder...")
    embedder = Embedder()

    print("Connecting to Qdrant...")
    qds = QdrantVectorStore()

    print("Creating sample embedding...")
    sample_vec = embedder.embed_texts(["test"])

    print("Preparing Qdrant collection...")
    vector_size = len(sample_vec[0]) if sample_vec else 384

    qds.delete_collection(qdrant_collection)
    qds.create_collection(
        collection_name=qdrant_collection,
        vector_size=vector_size
    )

    batch_points: List[Dict[str, Any]] = []
    contents: List[str] = []
    ids: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    doc_count = 0

    for doc_type, row in fetch_all_documents(engine):
        try:
            if doc_type == "commits":
                doc = DocumentBuilder.from_commit_row(row)
            elif doc_type == "prs":
                doc = DocumentBuilder.from_pr_row(row)
            elif doc_type == "issues":
                doc = DocumentBuilder.from_issue_row(row)
            else:
                continue
        except Exception as exc:
            logger.exception("Failed to build document for row: %s", exc)
            continue

        if not doc.content.strip():
            continue
            
        ids.append(doc.id)
        contents.append(doc.content)
        metadatas.append(doc.metadata.model_dump())

        if len(contents) >= BATCH_EMBED_SIZE:
            vectors = embedder.embed_texts(contents, batch_size=BATCH_EMBED_SIZE)
            for _id, vec, payload in zip(ids, vectors, metadatas):
                batch_points.append({"id": _id, "vector": vec, "payload": payload})
            qds.upsert_points(batch_points)
            batch_points = []
            contents = []
            ids = []
            metadatas = []

        doc_count += 1

        if doc_count % 100 == 0:
            print(f"Indexed {doc_count} docs...")

    # flush remainder
    if contents:
        vectors = embedder.embed_texts(contents, batch_size=BATCH_EMBED_SIZE)
        for _id, vec, payload, content in zip(ids, vectors, metadatas, contents):
            batch_points.append({
                "id": _id, 
                "vector": vec, 
                "payload": {
                    **payload,
                    "content": content
                }
            })
        qds.upsert_points(batch_points)


if __name__ == "__main__":
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise SystemExit("DATABASE_URL env var is required")
    index_documents(DATABASE_URL)

