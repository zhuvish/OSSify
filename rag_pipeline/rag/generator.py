import os
from groq import Groq
from dotenv import load_dotenv

from rag_pipeline.retrieval.retriever import Retriever

load_dotenv()

class RAGGenerator:
    def __init__(self):
        self.retriever = Retriever()

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def answer(self, query: str):
        results = self.retriever.search(query, top_k=2)

        context_blocks = []

        for result in results:
            payload = result["payload"]

            context_blocks.append(
                f"""
                    Document Type: {payload.get('document_type')}
                    SOURCE SCORE: {result.get('score')}
                    Content: {payload.get('content')}
                """
            )

        context = "\n\n".join(context_blocks)

        prompt = f"""
            You are a repository analysis assistant.

            IMPORTANT RULES:
            1. Answer ONLY from the provided repository context.
            2. Do NOT use general knowledge.
            3. If the context does not clearly answer the question, say:
            "The indexed repository context does not contain enough evidence."

            Repository Context:
            {context}

            Question:
            {query}
            """

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