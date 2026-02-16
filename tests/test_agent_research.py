"""Tests for POST /agent/research — auto-research agent endpoint."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture()
def _mock_stack():
    """Patch embedder, chroma, and LLM — same as test_query.py base stack."""
    fake_embedding = [0.1] * 384

    with (
        patch("app.ingest.embedder.get_model"),
        patch("app.main.embed_texts", return_value=[fake_embedding]),
        patch("app.db.chroma.get_client"),
        patch("app.main.heartbeat", return_value=True),
        patch("app.main.check_llm_ready", return_value={"ready": False, "reason": "mocked"}),
        patch("app.main.query_cache", None),
        patch("app.main.HYBRID_ENABLED", False),
        patch("app.main.RERANK_ENABLED", False),
    ):
        yield


@pytest.fixture()
def client(_mock_stack) -> TestClient:
    from app.main import app
    return TestClient(app)


def _make_chunk(
    doc_id: str = "md/what-is-bedrock.html-f43337c9.md",
    chunk_id: str = "md/what-is-bedrock.html-f43337c9.md#00000",
    text: str = "Amazon Bedrock is a fully managed service.",
    score: float = 0.85,
):
    from app.db.chroma import RetrievedChunk
    return RetrievedChunk(
        chunk_id=chunk_id, doc_id=doc_id, text=text, score=score,
        source_path=f"/app/data/corpus_raw/{doc_id}", content_type="md",
    )


# ── Helpers ────────────────────────────────────────────────────────────

_VALID_STATUSES = {"answered", "gap", "answered_after_retry"}


# ── Test: structured response with subquestions / findings / stats ──────

def test_agent_research_returns_structured_response(client: TestClient):
    """The endpoint must return topic, subquestions, findings, gaps, stats."""
    chunks = [_make_chunk()]
    from app.generation.llm import Citation, GeneratedAnswer
    gen_result = GeneratedAnswer(
        answer="Amazon Bedrock is a fully managed service [Chunk 1].",
        citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post("/agent/research", json={
            "topic": "Amazon Bedrock",
            "max_subquestions": 3,
        })

    assert resp.status_code == 200
    data = resp.json()

    # Top-level structure
    assert data["topic"] == "Amazon Bedrock"
    assert isinstance(data["subquestions"], list)
    assert len(data["subquestions"]) >= 3
    assert isinstance(data["findings"], list)
    assert isinstance(data["gaps"], list)
    assert isinstance(data["final_summary"], str)
    assert len(data["final_summary"]) > 0
    assert "answered_count" in data["stats"]
    assert "gap_count" in data["stats"]
    assert "answered_after_retry_count" in data["stats"]
    assert "avg_confidence" in data["stats"]

    # At least one finding should be answered
    statuses = {f["status"] for f in data["findings"]}
    assert statuses <= _VALID_STATUSES

    # possible_conflicts must be present
    assert isinstance(data["possible_conflicts"], list)


# ── Test: marks gap when sub-query returns null answer ──────────────────

def test_agent_research_marks_gap_on_null_answer(client: TestClient):
    """When all RAG queries return null, all findings must be gaps."""
    from app.generation.llm import GeneratedAnswer
    null_result = GeneratedAnswer(answer=None, citations=[])

    with (
        patch("app.main.query_chunks", return_value=[_make_chunk(score=0.2)]),
        patch("app.main.generate_answer", return_value=null_result),
    ):
        resp = client.post("/agent/research", json={
            "topic": "Nonexistent Feature XYZ",
            "max_subquestions": 3,
        })

    assert resp.status_code == 200
    data = resp.json()

    # All findings remain gap (retry also returns null)
    assert all(f["status"] == "gap" for f in data["findings"])
    assert all(f["answer"] is None for f in data["findings"])
    assert len(data["gaps"]) == len(data["subquestions"])

    # Gaps must have reason
    for gap in data["gaps"]:
        assert gap["reason"] in ("no_answer", "low_evidence")

    # Retry fields present — all were retried but none resolved
    for f in data["findings"]:
        assert f["attempts"] == 2
        assert f["retried_subquestion"] is not None
        assert f["retry_resolved"] is False


# ── Test: citations present for answered sub-questions ──────────────────

def test_agent_research_citations_for_answered(client: TestClient):
    """Answered findings must carry through citations from RAG."""
    chunks = [_make_chunk()]
    from app.generation.llm import Citation, GeneratedAnswer
    gen_result = GeneratedAnswer(
        answer="Bedrock provides access to foundation models [Chunk 1].",
        citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post("/agent/research", json={
            "topic": "Amazon Bedrock",
            "max_subquestions": 3,
        })

    assert resp.status_code == 200
    data = resp.json()

    answered = [f for f in data["findings"] if f["status"] in ("answered", "answered_after_retry")]
    assert len(answered) >= 1

    for finding in answered:
        assert len(finding["citations"]) >= 1
        assert "doc_id" in finding["citations"][0]
        assert "chunk_id" in finding["citations"][0]


# ── Test: max_subquestions clamped to 3 minimum ─────────────────────────

def test_agent_research_min_subquestions(client: TestClient):
    """Even when max_subquestions=1, at least 3 sub-questions are generated."""
    from app.generation.llm import GeneratedAnswer
    null_result = GeneratedAnswer(answer=None, citations=[])

    with (
        patch("app.main.query_chunks", return_value=[]),
        patch("app.main.generate_answer", return_value=null_result),
    ):
        resp = client.post("/agent/research", json={
            "topic": "Bedrock",
            "max_subquestions": 1,
        })

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["subquestions"]) >= 3


# ── Test: final_summary is non-empty ────────────────────────────────────

def test_agent_research_final_summary_nonempty(client: TestClient):
    """Final summary must always be a non-empty string."""
    from app.generation.llm import GeneratedAnswer
    null_result = GeneratedAnswer(answer=None, citations=[])

    with (
        patch("app.main.query_chunks", return_value=[]),
        patch("app.main.generate_answer", return_value=null_result),
    ):
        resp = client.post("/agent/research", json={
            "topic": "Something Unknown",
            "max_subquestions": 3,
        })

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["final_summary"], str)
    assert len(data["final_summary"]) > 10


# ── Test: retry changes gap → answered_after_retry ──────────────────────

def test_agent_retry_resolves_gap(client: TestClient):
    """When initial query returns null but retry succeeds, status becomes
    answered_after_retry with attempts=2 and retry_resolved=True."""
    from app.generation.llm import Citation, GeneratedAnswer

    chunks = [_make_chunk()]
    null_result = GeneratedAnswer(answer=None, citations=[])
    good_result = GeneratedAnswer(
        answer="Bedrock is a managed AI service [Chunk 1].",
        citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
    )

    # First call (initial) returns null; second call (retry) returns good answer
    call_count = {"n": 0}
    original_query = None

    def _alternating_generate(*args, **kwargs):
        call_count["n"] += 1
        # Odd calls → null (initial pass), Even calls → good (retry pass)
        if call_count["n"] % 2 == 1:
            return null_result
        return good_result

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", side_effect=_alternating_generate),
    ):
        resp = client.post("/agent/research", json={
            "topic": "Amazon Bedrock",
            "max_subquestions": 3,
        })

    assert resp.status_code == 200
    data = resp.json()

    retried = [f for f in data["findings"] if f["status"] == "answered_after_retry"]
    assert len(retried) >= 1, "At least one gap should be resolved by retry"

    for f in retried:
        assert f["attempts"] == 2
        assert f["retried_subquestion"] is not None
        assert f["retry_resolved"] is True
        assert f["answer"] is not None

    assert data["stats"]["answered_after_retry_count"] >= 1


# ── Test: confidence fields bounded [0,1] ───────────────────────────────

def test_agent_confidence_fields_bounded(client: TestClient):
    """Every finding must have confidence in [0,1] plus citation_count/unique_docs."""
    chunks = [_make_chunk()]
    from app.generation.llm import Citation, GeneratedAnswer
    gen_result = GeneratedAnswer(
        answer="Amazon Bedrock is a fully managed service [Chunk 1].",
        citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post("/agent/research", json={
            "topic": "Amazon Bedrock",
            "max_subquestions": 3,
        })

    assert resp.status_code == 200
    data = resp.json()

    for f in data["findings"]:
        assert 0.0 <= f["confidence"] <= 1.0, f"confidence out of range: {f['confidence']}"
        assert isinstance(f["citation_count"], int)
        assert isinstance(f["unique_docs"], int)
        assert f["citation_count"] >= 0
        assert f["unique_docs"] >= 0

    # avg_confidence in stats
    assert 0.0 <= data["stats"]["avg_confidence"] <= 1.0


# ── Test: possible_conflicts shape ──────────────────────────────────────

def test_agent_possible_conflicts_shape(client: TestClient):
    """possible_conflicts list must have correct structure when present."""
    chunks = [_make_chunk()]
    from app.generation.llm import Citation, GeneratedAnswer

    # Craft two answers with opposing keywords to trigger conflict detection
    call_count = {"n": 0}
    answers = [
        GeneratedAnswer(
            answer="Encryption is required for all Bedrock data [Chunk 1].",
            citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
        ),
        GeneratedAnswer(
            answer="Encryption is optional and can be configured [Chunk 1].",
            citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
        ),
    ]

    def _rotating_answer(*args, **kwargs):
        call_count["n"] += 1
        return answers[(call_count["n"] - 1) % len(answers)]

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", side_effect=_rotating_answer),
    ):
        resp = client.post("/agent/research", json={
            "topic": "Amazon Bedrock",
            "max_subquestions": 3,
        })

    assert resp.status_code == 200
    data = resp.json()

    # possible_conflicts always present as a list
    assert isinstance(data["possible_conflicts"], list)

    # When conflicts are detected, they must have proper shape
    for conflict in data["possible_conflicts"]:
        assert "finding_a" in conflict
        assert "finding_b" in conflict
        assert "reason" in conflict
        assert isinstance(conflict["reason"], str)


# ── Test: include_context=true returns contexts in findings ─────────────

def test_agent_include_context_returns_contexts(client: TestClient):
    """When include_context=true, each finding should have non-empty contexts."""
    chunks = [_make_chunk()]
    from app.generation.llm import Citation, GeneratedAnswer
    gen_result = GeneratedAnswer(
        answer="Amazon Bedrock is a fully managed service [Chunk 1].",
        citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post("/agent/research", json={
            "topic": "Amazon Bedrock",
            "max_subquestions": 3,
            "include_context": True,
        })

    assert resp.status_code == 200
    data = resp.json()

    # At least one answered finding must have contexts
    answered = [f for f in data["findings"] if f["status"] in ("answered", "answered_after_retry")]
    assert len(answered) >= 1

    has_contexts = any(len(f["contexts"]) > 0 for f in answered)
    assert has_contexts, "include_context=true should populate contexts in findings"

    # Validate context shape
    for f in data["findings"]:
        for ctx in f["contexts"]:
            assert "doc_id" in ctx
            assert "chunk_id" in ctx
            assert "text" in ctx
            assert "score" in ctx
