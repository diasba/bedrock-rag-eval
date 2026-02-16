"""LLM integration via Mistral API (OpenAI-compatible) with fallback."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.config import MISTRAL_API_KEY, MISTRAL_FALLBACK_MODELS, MISTRAL_MODEL, MISTRAL_TEMPERATURE
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
4. Answer concisely but completely (typically 1-3 sentences). For list questions, return the requested items clearly.
5. Do NOT paste or reproduce long spans of the context. Never include document headers like "Source:", "Fetched-At:", or large copied blocks.
6. If asked to list metrics/APIs/limits, provide the complete list found in context.
7. For compare/complementary questions, include both sides explicitly.
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
    """Check if Mistral API key is configured."""
    return bool(MISTRAL_API_KEY)


def check_llm_ready() -> dict:
    """Verify Mistral LLM is fully operational (key present + API probe).

    Returns:
        {"ready": bool, "reason": str}
    """
    if not MISTRAL_API_KEY:
        return {"ready": False, "reason": "MISTRAL_API_KEY not set"}

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=MISTRAL_API_KEY, base_url="https://api.mistral.ai/v1")
        last_reason = "No Mistral model candidates available"
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
                    return {"ready": True, "reason": f"Mistral API operational (model: {model})"}
                last_reason = f"Unexpected probe response from {model}: {text!r}"
            except Exception as exc:  # noqa: BLE001
                last_reason = f"Mistral API probe failed for {model}: {exc}"
        return {"ready": False, "reason": last_reason}
    except ImportError:
        return {"ready": False, "reason": "openai package not installed"}
    except Exception as exc:  # noqa: BLE001
        return {"ready": False, "reason": f"Mistral API probe failed: {exc}"}


def generate_answer(
    question: str,
    contexts: list[RetrievedChunk],
) -> GeneratedAnswer:
    """Generate an answer using Mistral LLM (or fallback if unavailable)."""
    if not is_llm_available():
        return _fallback_answer(contexts)

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=MISTRAL_API_KEY, base_url="https://api.mistral.ai/v1")
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
                    temperature=MISTRAL_TEMPERATURE,
                    max_tokens=1024,
                )

                answer = (completion.choices[0].message.content or "").strip()
                if not answer:
                    answer = "I don't know based on the provided documents."

                # If model says it doesn't know, comply with API contract
                if _is_unknown_answer(answer):
                    return GeneratedAnswer(answer=None, citations=[])

                citations = _extract_citations(answer, contexts)

                # Let caller apply citation fallback if model omitted markers.
                if not citations:
                    logger.info("LLM answer had no [Chunk N] markers; returning answer without citations")
                    return GeneratedAnswer(answer=answer, citations=[])

                return GeneratedAnswer(answer=answer, citations=citations)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning("LLM generation failed for model %s: %s", model, exc)

        if last_exc is not None:
            logger.warning("All Mistral models failed for generation; returning null answer")
        return _fallback_answer(contexts)
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM generation failed: %s", exc)
        return _fallback_answer(contexts)


def generate_answer_stream(
    question: str,
    contexts: list[RetrievedChunk],
):
    """Stream answer tokens from Mistral LLM.

    Yields dicts:
      ``{"type": "token", "token": "..."}`` — partial token
      ``{"type": "done", "answer": str|None, "citations": list}`` — final
    """
    if not is_llm_available():
        yield {"type": "done", "answer": None, "citations": []}
        return

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=MISTRAL_API_KEY, base_url="https://api.mistral.ai/v1")
        user_prompt = _build_user_prompt(question, contexts)

        for model in _candidate_models():
            try:
                stream = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=MISTRAL_TEMPERATURE,
                    max_tokens=1024,
                    stream=True,
                )

                full_answer = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    token = delta.content if delta and delta.content else ""
                    if token:
                        full_answer += token
                        yield {"type": "token", "token": token}

                full_answer = full_answer.strip()
                if not full_answer or _is_unknown_answer(full_answer):
                    yield {"type": "done", "answer": None, "citations": []}
                    return

                citations = _extract_citations(full_answer, contexts)
                if not citations:
                    logger.info("Streamed answer had no [Chunk N] markers; returning answer without citations")
                    yield {"type": "done", "answer": full_answer, "citations": []}
                    return

                yield {
                    "type": "done",
                    "answer": full_answer,
                    "citations": [
                        {"doc_id": c.doc_id, "chunk_id": c.chunk_id} for c in citations
                    ],
                }
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("Streaming failed for model %s: %s", model, exc)

        yield {"type": "done", "answer": None, "citations": []}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Streaming generation failed: %s", exc)
        yield {"type": "done", "answer": None, "citations": []}


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
    for model in [MISTRAL_MODEL, *MISTRAL_FALLBACK_MODELS]:
        if model and model not in seen:
            models.append(model)
            seen.add(model)
    return models
