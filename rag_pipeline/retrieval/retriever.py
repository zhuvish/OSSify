from rag_pipeline.embeddings.embedder import Embedder
from rag_pipeline.vector_store.qdrant_client import QdrantVectorStore


class Retriever:
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = QdrantVectorStore(
            default_collection="repo_documents"
        )

    def search(self, query: str, top_k: int = 5):
        query_vector = self.embedder.embed_texts([query])[0]

        results = self.vector_store.semantic_search(
            query_vector=query_vector,
            top_k=top_k
        )

        return results