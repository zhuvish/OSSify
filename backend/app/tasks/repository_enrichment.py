from graph.builders.build_graph import build_graph
from rag_pipeline.indexing.index_contributor_documents import index_documents

from dotenv import load_dotenv
import os

load_dotenv()


def run_repository_enrichment():

    print("=" * 50)
    print("Starting Repository Enrichment")
    print("=" * 50)

    print("Building Knowledge Graph...")
    build_graph()

    print("Building Embeddings...")
    index_documents(
        database_url=os.getenv("DATABASE_URL")
    )

    print("Repository Enrichment Complete")