"""LLM integration via Groq API with fallback for missing keys."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE
from app.db.chroma import RetrievedChunk

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """A reference to a source document chunk."""

    doc_id: str
    chunk_id: str


@dataclass
class GeneratedAnswer:
    """Result of LLM generation."""

    answer: str
    citations: list[Citation]


# ── Prompt template ────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a precise assistant answering questions about AWS Bedrock documentation.

Rules:
1. Answer ONLY using the provided context chunks.
2. If the context doesn't contain enough information, say "I don't know based on the provided documents."
3. Cite sources by referencing [Chunk N] where N is the chunk number from the context.
4. Be concise and accurate.
5. Do not make assumptions or add information not present in the context."""


def _build_user_prompt(question: str, contexts: list[RetrievedChunk]) -> str:
    """Build the user prompt with numbered context chunks."""
    context_text = "\n\n".join(
        f"[Chunk {i+1}] (doc: {c.doc_id}, id: {c.chunk_id})\n{c.text}"
        for i, c in enumerate(contexts)
    )
    return f"""Context:
{context_text}

Question: {question}

Answer:"""


def _extract_citations(answer: str, contexts: list[RetrievedChunk]) -> list[Citation]:
    """Extract [Chunk N] references from answer and map to actual chunk IDs."""
    citations: list[Citation] = []
    seen: set[str] = set()

    # Find all [Chunk N] patterns
    matches = re.findall(r"\[Chunk (\d+)\]", answer)

    for match in matches:
        idx = int(match) - 1  # Convert to 0-based index
        if 0 <= idx < len(contexts):
            chunk = contexts[idx]
            if chunk.chunk_id not in seen:
                citations.append(Citation(doc_id=chunk.doc_id, chunk_id=chunk.chunk_id))
                seen.add(chunk.chunk_id)

    return citations


# ── Generation functions ───────────────────────────────────────────────

def is_llm_available() -> bool:
    """Check if Groq API key is configured."""
    return bool(GROQ_API_KEY)


def generate_answer(
    question: str,
    contexts: list[RetrievedChunk],
) -> GeneratedAnswer:
    """Generate an answer using Groq LLM (or fallback if unavailable)."""
    if not is_llm_available():
        return _fallback_answer(contexts)

    try:
        # Lazy import to avoid errors if groq not installed
        from groq import Groq  # type: ignore

        client = Groq(api_key=GROQ_API_KEY)

        user_prompt = _build_user_prompt(question, contexts)

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=GROQ_TEMPERATURE,
            max_tokens=1024,
        )

        answer = completion.choices[0].message.content or ""
        citations = _extract_citations(answer, contexts)

        return GeneratedAnswer(answer=answer, citations=citations)

    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM generation failed: %s", exc)
        return _fallback_answer(contexts)


def _fallback_answer(contexts: list[RetrievedChunk]) -> GeneratedAnswer:
    """Fallback response when LLM is unavailable."""
    if not contexts:
        return GeneratedAnswer(
            answer="I don't know based on the provided documents.",
            citations=[],
        )

    # Simple concatenation fallback
    answer = "Retrieved context (LLM unavailable):\n\n" + "\n\n---\n\n".join(
        f"[{c.doc_id}]\n{c.text[:300]}..." for c in contexts[:2]
    )

    citations = [Citation(doc_id=c.doc_id, chunk_id=c.chunk_id) for c in contexts[:2]]

    return GeneratedAnswer(answer=answer, citations=citations)
