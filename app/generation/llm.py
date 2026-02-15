"""LLM integration via Groq API with fallback for missing keys."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.config import GROQ_API_KEY, GROQ_FALLBACK_MODELS, GROQ_MODEL, GROQ_TEMPERATURE
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

    answer: str | None
    citations: list[Citation]


# ── Prompt template ────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a precise assistant answering questions about AWS Bedrock documentation.

Rules:
1. Answer ONLY using the provided context chunks.
2. If the context doesn't contain enough information to answer, respond with exactly: I don't know based on the provided documents.
3. Cite sources using [Chunk N] where N is the chunk number from the context.
4. Answer in 1-2 sentences maximum.
5. Do NOT paste or reproduce long spans of the context. Never include document headers like "Source:", "Fetched-At:", or large copied blocks.
6. Prefer concise, definitional phrasing for "what is" questions.
7. If asked to list metrics/APIs/limits, provide the complete list found in context.
8. Do not add assumptions or information not present in the context.
9. Do not include section titles, markdown headings, or boilerplate text in your answer."""


_UNKNOWN_PATTERNS = [
    r"^i don't know based on the provided documents\.?$",
    r"^i do not know based on the provided documents\.?$",
    r"^i don't know\.?$",
    r"^not enough information.*$",
    r"^insufficient context\.?$",
    r"^insufficient information\.?$",
    r"^no relevant information\.?$",
    r"^cannot (answer|determine|be answered).*$",
    r"^unable to (answer|determine).*$",
    r"^the (provided )?context (is )?(insufficient|does not).*$",
    r"^there is (not enough|insufficient).*$",
    r"^based on the (provided )?(context|documents?),? (i )?(cannot|can't|don't).*$",
]


def _is_unknown_answer(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return True
    return any(re.match(p, t) for p in _UNKNOWN_PATTERNS)


def _sanitize_context(text: str, max_chars: int = 1200) -> str:
    """Remove boilerplate and cap length to reduce doc-dumps."""
    if not text:
        return ""

    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        # Drop common boilerplate from crawled MD/TXT
        if line.lower().startswith(("source:", "fetched-at:", "title:", "url:")):
            continue
        if line in ("---", "___", "***"):
            continue
        # Drop obvious markdown headings to reduce copying
        if line.startswith("#"):
            continue

        lines.append(line)

    cleaned = " ".join(lines)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:max_chars]


def _build_user_prompt(question: str, contexts: list[RetrievedChunk]) -> str:
    """Build the user prompt with numbered context chunks."""
    context_text = "\n\n".join(
        f"[Chunk {i+1}] (doc: {c.doc_id}, id: {c.chunk_id})\n{_sanitize_context(c.text)}"
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


def check_llm_ready() -> dict:
    """Verify Groq LLM is fully operational (key present + API probe).

    Returns:
        {"ready": bool, "reason": str}
    """
    if not GROQ_API_KEY:
        return {"ready": False, "reason": "GROQ_API_KEY not set"}

    try:
        from groq import Groq  # type: ignore

        client = Groq(api_key=GROQ_API_KEY)
        last_reason = "No Groq model candidates available"
        for model in _candidate_models():
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Return exactly the word OK."}],
                    temperature=0.0,
                    max_tokens=8,
                )
                text = (completion.choices[0].message.content or "").strip()
                if "OK" in text.upper():
                    return {"ready": True, "reason": f"Groq API operational (model: {model})"}
                last_reason = f"Unexpected probe response from {model}: {text!r}"
            except Exception as exc:  # noqa: BLE001
                last_reason = f"Groq API probe failed for {model}: {exc}"
        return {"ready": False, "reason": last_reason}
    except ImportError:
        return {"ready": False, "reason": "groq package not installed"}
    except Exception as exc:  # noqa: BLE001
        return {"ready": False, "reason": f"Groq API probe failed: {exc}"}


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
        last_exc: Exception | None = None

        for model in _candidate_models():
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=GROQ_TEMPERATURE,
                    max_tokens=1024,
                )

                answer = (completion.choices[0].message.content or "").strip()
                if not answer:
                    answer = "I don't know based on the provided documents."

                # If model says it doesn't know, comply with API contract
                if _is_unknown_answer(answer):
                    return GeneratedAnswer(answer=None, citations=[])

                citations = _extract_citations(answer, contexts)

                # Hard guard: require at least one citation for non-null answers
                if not citations:
                    return GeneratedAnswer(answer=None, citations=[])

                return GeneratedAnswer(answer=answer, citations=citations)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning("LLM generation failed for model %s: %s", model, exc)

        if last_exc is not None:
            logger.warning("All Groq models failed for generation; returning null answer")
        return _fallback_answer(contexts)
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM generation failed: %s", exc)
        return _fallback_answer(contexts)


def _fallback_answer(_contexts: list[RetrievedChunk]) -> GeneratedAnswer:
    """Fallback response when LLM is unavailable.

    Strict contract: always returns answer=None, citations=[].
    The caller (/query endpoint) is responsible for deciding how to
    present a null answer to the user.
    """
    return GeneratedAnswer(answer=None, citations=[])


def _candidate_models() -> list[str]:
    """Primary model followed by optional fallbacks without duplicates."""
    models: list[str] = []
    seen: set[str] = set()
    for model in [GROQ_MODEL, *GROQ_FALLBACK_MODELS]:
        if model and model not in seen:
            models.append(model)
            seen.add(model)
    return models