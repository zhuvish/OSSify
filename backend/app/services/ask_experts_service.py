"""Expert Q&A service that answers natural language questions about contributors.

Pipeline:
  1. Use existing find_experts() to retrieve relevant experts for the question
  2. Use existing Groq LLM to generate a structured response (summary, relevant info, answer)

Reuses existing expert retrieval and LLM infrastructure — no duplicate logic.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from backend.app.services.expert_retrieval_service import find_experts

logger = logging.getLogger(__name__)


def ask_experts(question: str, top_k: int = 5) -> Dict[str, Any]:
    """Answer a natural language question about expert contributors.

    Pipeline:
      1. Retrieve top experts using existing find_experts()
      2. Build context from retrieved expert data
      3. Use existing Groq LLM to generate structured response
      4. Return summary, relevant_information, and answer

    Args:
        question: Natural language question (e.g., "Who should review backend API changes?")
        top_k: Number of top experts to retrieve (default 5)

    Returns:
        Dict with keys:
          - summary: Brief summary of the findings
          - relevant_information: List of bullet-point facts
          - answer: Full grounded answer
    """
    # Step 1: Retrieve experts using existing infrastructure
    experts = find_experts(query=question, top_k=top_k)

    if not experts:
        return {
            "summary": "No matching experts found.",
            "relevant_information": [],
            "answer": f"No experts found matching your question about \"{question}\". Try rephrasing your question.",
        }

    # Step 2: Build structured context from expert data
    context_lines = []
    for i, expert in enumerate(experts, 1):
        username = expert.get("username", "unknown")
        expertise = expert.get("expertise", "N/A")
        score = expert.get("score", 0)
        confidence = expert.get("confidence", 0)
        matched_docs = expert.get("matched_documents", 0)
        expertise_areas = expert.get("expertise_areas", [])

        areas_str = ", ".join(
            f"{a['domain']} ({a['score']:.1f})"
            for a in expertise_areas[:5]
        )
        context_lines.append(
            f"Expert {i}: {username}\n"
            f"  Primary Expertise: {expertise}\n"
            f"  Relevance Score: {score:.2f}\n"
            f"  Confidence: {confidence:.0%}\n"
            f"  Matched Documents: {matched_docs}\n"
            f"  Expertise Areas: {areas_str}\n"
        )

    context = "\n".join(context_lines)

    # Step 3: Generate answer using existing Groq LLM
    answer = _generate_qa_answer(question, context)

    # Step 4: Parse structured response
    parsed = _parse_structured_answer(answer, experts)

    return parsed


def _generate_qa_answer(question: str, context: str) -> str:
    """Generate a structured answer using the existing Groq LLM."""
    if not os.getenv("GROQ_API_KEY"):
        return _fallback_answer(question)

    try:
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""You are an expert discovery assistant for an open-source repository analysis tool.

Given a question about contributors and a list of matched experts, produce a structured response.

RULES:
1. Answer ONLY from the provided expert data. Do NOT hallucinate contributors or facts.
2. Be specific — reference usernames, scores, and expertise areas.
3. If no experts clearly match, say so.

QUESTION:
{question}

RETRIEVED EXPERTS (ranked by relevance):
{context}

OUTPUT FORMAT:
Summary: <2-3 sentence overview of who the relevant experts are and why>
Relevant Information:
- <bullet point with specific fact about an expert>
- <bullet point with specific fact about an expert>
- <bullet point with specific fact about an expert>
Answer: <2-4 sentence final answer recommending or explaining the expert>
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.exception("LLM call failed for ask_experts")
        return _fallback_answer(question)


def _fallback_answer(question: str) -> str:
    """Provide a structured fallback answer when LLM is unavailable."""
    # This tries to give something useful even without LLM
    from backend.app.services.expert_retrieval_service import find_experts

    experts = find_experts(query=question, top_k=3)
    if not experts:
        return (
            f"Summary: No experts found.\n"
            f"Relevant Information:\n"
            f"- No matched experts for this question.\n"
            f"Answer: No relevant experts could be identified. Try a different question."
        )

    lines = []
    lines.append(f"Summary: Found {len(experts)} relevant expert(s) for your question.")
    lines.append("Relevant Information:")
    for expert in experts:
        username = expert.get("username", "unknown")
        expertise = expert.get("expertise", "N/A")
        confidence = expert.get("confidence", 0)
        matched = expert.get("matched_documents", 0)
        lines.append(f"- {username} (expertise: {expertise}, confidence: {confidence:.0%}, {matched} matched documents)")

    top = experts[0]
    lines.append(
        f"Answer: {top['username']} is the top-ranked expert for this topic "
        f"with expertise in {top['expertise']}. "
        f"Confidence: {top['confidence']:.0%} with {top['matched_documents']} matched documents."
    )
    return "\n".join(lines)


def _parse_structured_answer(raw_answer: str, experts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Parse the LLM's structured answer into summary, relevant_information, and answer fields."""
    summary = ""
    relevant_info: List[str] = []
    answer = ""

    lines = raw_answer.strip().split("\n")
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        lower = stripped.lower()

        if lower.startswith("summary:"):
            current_section = "summary"
            summary = stripped[len("summary:"):].strip()
        elif lower.startswith("relevant information:"):
            current_section = "relevant"
        elif lower.startswith("answer:"):
            current_section = "answer"
            answer = stripped[len("answer:"):].strip()
        elif current_section == "summary":
            summary += " " + stripped
        elif current_section == "relevant":
            if stripped.startswith("-") or stripped.startswith("*"):
                relevant_info.append(stripped.lstrip("-* ").strip())
            else:
                relevant_info.append(stripped)
        elif current_section == "answer":
            answer += " " + stripped

    # Fallback if parsing failed
    if not summary and not relevant_info and not answer:
        top = experts[0] if experts else {"username": "N/A", "expertise": "N/A"}
        summary = f"Found {len(experts)} relevant expert(s)."
        relevant_info = [
            f"{e['username']} - {e['expertise']} (confidence: {e['confidence']:.0%})"
            for e in experts[:3]
        ]
        answer = f"{top['username']} is the top expert with {top['confidence']:.0%} confidence score."

    return {
        "summary": summary.strip(),
        "relevant_information": relevant_info[:5],
        "answer": answer.strip(),
    }