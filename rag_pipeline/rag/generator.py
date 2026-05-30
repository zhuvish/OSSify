import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from rag_pipeline.retrieval.retriever import Retriever

load_dotenv()


class RAGGenerator:
    """RAG generator with support for global and contributor-grounded retrieval."""

    def __init__(self):
        self.retriever = Retriever()
        self.client = None
        if os.getenv("GROQ_API_KEY"):
            try:
                from groq import Groq
                self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            except ImportError:
                pass

    def answer(
        self,
        query: str,
        contributor_id: Optional[int] = None,
        top_k: int = 2
    ) -> Dict[str, Any]:
        """Answer a question with optional contributor grounding.

        Args:
            query: Question to answer
            contributor_id: If provided, search ONLY this contributor's documents
            top_k: Number of documents to retrieve

        Returns:
            Dictionary with answer, evidence, and grounding info
        """
        # Retrieve documents (optionally filtered by contributor)
        if contributor_id is not None:
            results = self.retriever.search_by_contributor(
                query=query,
                contributor_id=contributor_id,
                top_k=top_k
            )
            grounding_type = "contributor_scoped"
        else:
            results = self.retriever.search(query, top_k=top_k)
            grounding_type = "global"

        if not results:
            return {
                "answer": "No relevant documents found.",
                "evidence": [],
                "grounding_type": grounding_type,
                "query": query
            }

        # Build context from retrieved documents
        context_blocks = []
        evidence = []

        for i, result in enumerate(results, 1):
            payload = result["payload"]
            context_blocks.append(
                f"""[Document {i}]
Document Type: {payload.get('document_type')}
Source Score: {result.get('score', 0):.4f}
Content: {payload.get('content', '')}"""
            )

            evidence.append({
                "document_type": payload.get("document_type"),
                "score": result.get("score", 0),
                "content_snippet": payload.get("content", "")[:300],
                "commit_sha": payload.get("commit_sha"),
                "pr_number": payload.get("pr_number"),
                "issue_number": payload.get("issue_number")
            })

        context = "\n\n".join(context_blocks)

        # Generate answer
        answer = self._generate_answer(query, context, contributor_id)

        return {
            "answer": answer,
            "evidence": evidence,
            "grounding_type": grounding_type,
            "query": query,
            "document_count": len(results)
        }

    def _generate_answer(
        self,
        query: str,
        context: str,
        contributor_id: Optional[int] = None
    ) -> str:
        """Generate an answer using the LLM."""
        if not self.client:
            return "LLM not configured - cannot generate response."

        prompt = f"""You are a repository analysis assistant.

IMPORTANT RULES:
1. Answer ONLY from the provided repository context.
2. Do NOT use general knowledge.
3. If the context does not clearly answer the question, say:
"The indexed repository context does not contain enough evidence."
{"4. Focus specifically on the contributor's work and contributions." if contributor_id else ""}

Repository Context:
{context}

Question:
{query}
"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def answer_with_contributor_grounding(
        self,
        query: str,
        contributor_id: int,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Answer a question using ONLY a specific contributor's documents.

        This is a convenience method for contributor-grounded RAG.

        Args:
            query: Question to answer
            contributor_id: Local PostgreSQL contributor ID
            top_k: Number of documents to retrieve

        Returns:
            Dictionary with answer, evidence, and grounding info
        """
        return self.answer(
            query=query,
            contributor_id=contributor_id,
            top_k=top_k
        )
