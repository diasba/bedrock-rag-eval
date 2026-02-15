"""Unit tests for /query endpoint — mocked retrieval + LLM layer.

These tests never import sentence-transformers or torch; they patch
the embedder and chroma modules so the test suite runs in <1 s with
zero external dependencies.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture()
def _mock_stack():
    """Patch embedder, chroma, and LLM so no real models are loaded."""
    fake_embedding = [0.1] * 384  # all-MiniLM-L6-v2 dimension

    with (
        patch("app.ingest.embedder.get_model"),
        patch("app.main.embed_texts", return_value=[fake_embedding]) as mock_embed,
        patch("app.db.chroma.get_client"),
        patch("app.main.heartbeat", return_value=True),
    ):
        yield mock_embed


@pytest.fixture()
def client(_mock_stack) -> TestClient:
    from app.main import app
    return TestClient(app)


def _make_retrieved_chunk(
    doc_id: str = "txt/bedrock_runtime_metrics.txt",
    chunk_id: str = "txt/bedrock_runtime_metrics.txt#00000",
    text: str = "Metric: Invocations. Number of successful requests.",
    score: float = 0.85,
):
    """Build a RetrievedChunk without importing at module level."""
    from app.db.chroma import RetrievedChunk

    return RetrievedChunk(
        chunk_id=chunk_id,
        doc_id=doc_id,
        text=text,
        score=score,
        source_path=f"/app/data/corpus_raw/{doc_id}",
        content_type="txt",
    )


# ── Test: answerable question returns citations ────────────────────────

def test_query_answerable_returns_citations(client: TestClient):
    """When retrieval returns relevant chunks and LLM responds with markers,
    the endpoint must return a non-empty answer with citations."""
    chunks = [
        _make_retrieved_chunk(score=0.85),
        _make_retrieved_chunk(
            doc_id="txt/bedrock_invoke_streaming_support.txt",
            chunk_id="txt/bedrock_invoke_streaming_support.txt#00000",
            text="Some Amazon Bedrock Runtime API operations support streaming.",
            score=0.72,
        ),
    ]

    llm_answer = "Amazon Bedrock tracks Invocations and other metrics [Chunk 1]."

    from app.generation.llm import Citation, GeneratedAnswer

    gen_result = GeneratedAnswer(
        answer=llm_answer,
        citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post("/query", json={"question": "What metrics does Bedrock provide?"})

    assert resp.status_code == 200
    data = resp.json()

    assert data["answer"] == llm_answer
    assert len(data["citations"]) >= 1
    assert data["citations"][0]["chunk_id"] == chunks[0].chunk_id


# ── Test: no-answer gate triggers on low score ─────────────────────────

def test_query_no_answer_low_score(client: TestClient):
    """When the best retrieval score is below threshold, must return the
    no-answer string and empty citations."""
    low_score_chunk = _make_retrieved_chunk(score=0.1)

    with patch("app.main.query_chunks", return_value=[low_score_chunk]):
        resp = client.post("/query", json={"question": "What is the price of AWS Lambda?"})

    assert resp.status_code == 200
    data = resp.json()

    assert data["answer"] == "I don't know based on the provided documents."
    assert data["citations"] == []


# ── Test: no-answer gate triggers on empty retrieval ───────────────────

def test_query_no_answer_empty_retrieval(client: TestClient):
    """When retrieval returns nothing, must return the no-answer string."""
    with patch("app.main.query_chunks", return_value=[]):
        resp = client.post("/query", json={"question": "Unrelated question?"})

    assert resp.status_code == 200
    data = resp.json()

    assert data["answer"] == "I don't know based on the provided documents."
    assert data["citations"] == []


# ── Test: citation fallback when LLM omits markers ────────────────────

def test_query_citation_fallback_when_llm_omits_markers(client: TestClient):
    """If LLM answers but omits [Chunk N] markers, endpoint must still
    return citations by falling back to all retrieved chunks."""
    chunks = [_make_retrieved_chunk(score=0.85)]

    from app.generation.llm import GeneratedAnswer

    gen_result = GeneratedAnswer(
        answer="Amazon Bedrock provides several runtime metrics.",
        citations=[],  # LLM omitted markers
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post("/query", json={"question": "What metrics does Bedrock provide?"})

    assert resp.status_code == 200
    data = resp.json()

    # Answer is real (not the no-answer string)
    assert "I don't know" not in data["answer"]
    # Fallback must have cited the retrieved chunks
    assert len(data["citations"]) == 1
    assert data["citations"][0]["chunk_id"] == chunks[0].chunk_id


# ── Test: include_context flag ─────────────────────────────────────────

def test_query_include_context_returns_retrieved(client: TestClient):
    """When include_context=true, retrieved field must be populated."""
    chunks = [_make_retrieved_chunk(score=0.85)]

    from app.generation.llm import Citation, GeneratedAnswer

    gen_result = GeneratedAnswer(
        answer="Answer [Chunk 1].",
        citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post(
            "/query",
            json={"question": "metrics?", "include_context": True},
        )

    assert resp.status_code == 200
    data = resp.json()

    assert data["retrieved"] is not None
    assert len(data["retrieved"]) == 1
    assert "text" in data["retrieved"][0]
    assert "score" in data["retrieved"][0]
