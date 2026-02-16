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
    assert len(data["findings"]) == len(data["subquestions"])
    assert isinstance(data["gaps"], list)
    assert isinstance(data["final_summary"], str)
    assert len(data["final_summary"]) > 0
    assert "answered_count" in data["stats"]
    assert "gap_count" in data["stats"]

    # At least one finding should be answered (LLM mock returns answers)
    statuses = [f["status"] for f in data["findings"]]
    assert "answered" in statuses


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

    assert data["stats"]["gap_count"] == len(data["subquestions"])
    assert data["stats"]["answered_count"] == 0
    assert all(f["status"] == "gap" for f in data["findings"])
    assert all(f["answer"] is None for f in data["findings"])
    assert len(data["gaps"]) == len(data["subquestions"])

    # Gaps must have reason
    for gap in data["gaps"]:
        assert gap["reason"] in ("no_answer", "low_evidence")


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

    answered = [f for f in data["findings"] if f["status"] == "answered"]
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
