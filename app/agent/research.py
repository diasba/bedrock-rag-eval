"""Auto-Research Agent — generates sub-questions, queries RAG, synthesises report.

MVP implementation: template-based sub-question generation with lightweight
deduplication, internal RAG pipeline calls (no HTTP round-trips), and an
optional LLM synthesis step with deterministic fallback.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from app.config import MISTRAL_API_KEY, MISTRAL_MODEL, MISTRAL_FALLBACK_MODELS, MISTRAL_TEMPERATURE

logger = logging.getLogger(__name__)

# ── Sub-question templates ─────────────────────────────────────────────
# Each template is format()-ed with ``topic``.  Deterministic, no LLM needed.

_TEMPLATES: list[str] = [
    "What is {topic}?",
    "What are the key features of {topic}?",
    "How does {topic} work?",
    "What are the limitations or constraints of {topic}?",
    "How do you get started with {topic}?",
    "What APIs or operations are available for {topic}?",
    "What are common use cases for {topic}?",
    "What security or access controls does {topic} provide?",
]


@dataclass
class Finding:
    subquestion: str
    answer: str | None
    citations: list[dict[str, str]]
    status: str  # "answered" | "gap"
    contexts: list[dict] = field(default_factory=list)


@dataclass
class Gap:
    subquestion: str
    reason: str  # "no_answer" | "low_evidence"


@dataclass
class ResearchResult:
    topic: str
    subquestions: list[str]
    findings: list[Finding]
    gaps: list[Gap]
    final_summary: str
    stats: dict[str, int]


# ── Sub-question generation ────────────────────────────────────────────


def generate_subquestions(topic: str, max_subquestions: int = 5) -> list[str]:
    """Generate diverse sub-questions from a topic using templates.

    Clamps output to ``[3, max_subquestions]``.  Deduplicates by
    normalised prefix to avoid near-identical questions.
    """
    limit = max(3, min(max_subquestions, len(_TEMPLATES)))
    raw = [tpl.format(topic=topic) for tpl in _TEMPLATES[:limit]]

    # Lightweight dedup: skip questions whose first 40 chars (lowered) collide
    seen: set[str] = set()
    deduped: list[str] = []
    for q in raw:
        key = q[:40].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(q)
    return deduped[:limit]


# ── Internal RAG query (no HTTP) ───────────────────────────────────────


def _query_rag(question: str, top_k: int = 4, include_context: bool = False) -> dict:
    """Call the existing /query pipeline internally and return a plain dict.

    Reuses the FastAPI handler directly — no HTTP round-trip, no new deps.
    """
    from app.main import query as _query_fn, QueryRequest  # lazy to avoid circular

    body = QueryRequest(question=question, top_k=top_k, include_context=include_context)
    response = _query_fn(body)
    return response.model_dump()


# ── Research pipeline ──────────────────────────────────────────────────


def run_research(
    topic: str,
    max_subquestions: int = 5,
    top_k: int = 4,
    include_context: bool = False,
) -> ResearchResult:
    """Execute the full auto-research pipeline.

    1. Generate sub-questions from *topic*.
    2. Query existing RAG for each.
    3. Classify findings / gaps.
    4. Synthesise a summary (LLM or fallback).
    """
    subquestions = generate_subquestions(topic, max_subquestions)
    logger.info("Research agent: %d sub-questions for topic=%r", len(subquestions), topic)

    findings: list[Finding] = []
    gaps: list[Gap] = []

    for sq in subquestions:
        try:
            result = _query_rag(sq, top_k=top_k, include_context=include_context)
        except Exception as exc:  # noqa: BLE001
            logger.warning("RAG query failed for sub-question %r: %s", sq, exc)
            result = {"answer": None, "citations": []}

        answer = result.get("answer")
        citations = result.get("citations") or []
        contexts = result.get("retrieved") or []

        if answer is None:
            findings.append(Finding(
                subquestion=sq,
                answer=None,
                citations=[],
                status="gap",
                contexts=contexts,
            ))
            gaps.append(Gap(subquestion=sq, reason="no_answer"))
        elif not citations:
            # Answer exists but no grounding — low evidence
            findings.append(Finding(
                subquestion=sq,
                answer=answer,
                citations=[],
                status="gap",
                contexts=contexts,
            ))
            gaps.append(Gap(subquestion=sq, reason="low_evidence"))
        else:
            findings.append(Finding(
                subquestion=sq,
                answer=answer,
                citations=citations,
                status="answered",
                contexts=contexts,
            ))

    answered_count = sum(1 for f in findings if f.status == "answered")
    gap_count = sum(1 for f in findings if f.status == "gap")

    # ── Synthesis ──────────────────────────────────────────────────
    final_summary = _synthesise_summary(topic, findings)

    return ResearchResult(
        topic=topic,
        subquestions=subquestions,
        findings=findings,
        gaps=gaps,
        final_summary=final_summary,
        stats={"answered_count": answered_count, "gap_count": gap_count},
    )


# ── Summary synthesis ──────────────────────────────────────────────────

_SYNTHESIS_SYSTEM = (
    "You are a research assistant. Given a topic and a list of findings "
    "(question/answer pairs), produce a concise 3-5 sentence summary that "
    "covers the key points. Mention any gaps where information was missing. "
    "Do not invent facts beyond the provided findings."
)


def _synthesise_summary(topic: str, findings: list[Finding]) -> str:
    """Build a final summary — LLM-backed when available, else deterministic."""
    answered = [f for f in findings if f.status == "answered" and f.answer]
    gap_questions = [f.subquestion for f in findings if f.status == "gap"]

    # Fast deterministic fallback
    if not answered:
        return (
            f"No information was found in the corpus for the topic \"{topic}\". "
            f"All {len(findings)} sub-questions resulted in knowledge gaps."
        )

    # Try LLM synthesis
    if MISTRAL_API_KEY:
        try:
            return _llm_synthesise(topic, answered, gap_questions)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM synthesis failed, using fallback: %s", exc)

    # Deterministic fallback
    return _deterministic_summary(topic, answered, gap_questions)


def _deterministic_summary(
    topic: str,
    answered: list[Finding],
    gap_questions: list[str],
) -> str:
    """Stitch answered findings into a readable paragraph."""
    parts = [f"Research on \"{topic}\" found {len(answered)} answered sub-questions."]
    for f in answered[:5]:
        # Take first sentence of each answer
        first_sentence = (f.answer or "").split(". ")[0].rstrip(".")
        if first_sentence:
            parts.append(f"{first_sentence}.")
    if gap_questions:
        parts.append(
            f"Knowledge gaps remain for: {'; '.join(gap_questions[:3])}."
        )
    return " ".join(parts)


def _llm_synthesise(
    topic: str,
    answered: list[Finding],
    gap_questions: list[str],
) -> str:
    """Use Mistral to synthesise findings into a summary."""
    from openai import OpenAI  # type: ignore

    findings_text = "\n".join(
        f"Q: {f.subquestion}\nA: {f.answer}"
        for f in answered[:6]
    )
    gaps_text = (
        "\nGaps (no answer found): " + "; ".join(gap_questions[:3])
        if gap_questions else ""
    )

    user_prompt = f"Topic: {topic}\n\nFindings:\n{findings_text}{gaps_text}\n\nSummary:"

    client = OpenAI(api_key=MISTRAL_API_KEY, base_url="https://api.mistral.ai/v1")

    models = [MISTRAL_MODEL] + [m for m in MISTRAL_FALLBACK_MODELS if m != MISTRAL_MODEL]
    for model in models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _SYNTHESIS_SYSTEM},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=MISTRAL_TEMPERATURE,
                max_tokens=512,
            )
            text = (completion.choices[0].message.content or "").strip()
            if text:
                return text
        except Exception:  # noqa: BLE001
            continue

    # All models failed — fall back
    return _deterministic_summary(topic, answered, gap_questions)
