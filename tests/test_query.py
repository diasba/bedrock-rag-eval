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
        patch("app.main.check_llm_ready", return_value={"ready": False, "reason": "mocked"}),
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


# ── Test: low scores no longer force null answers ──────────────────────

def test_query_low_score_still_generates(client: TestClient):
    """If retrieval returns chunks, endpoint should still generate."""
    low_score_chunk = _make_retrieved_chunk(score=0.1)
    from app.generation.llm import GeneratedAnswer

    gen_result = GeneratedAnswer(
        answer="I don't know based on the provided documents.",
        citations=[],
    )

    with (
        patch("app.main.query_chunks", return_value=[low_score_chunk]),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post(
            "/query",
            json={"question": "What is the price of AWS Lambda?", "include_context": True},
        )

    assert resp.status_code == 200
    data = resp.json()

    assert data["answer"] is None
    assert data["citations"] == []
    assert data["retrieved_count"] == 1
    assert data["gate_reason"] == "generated_no_answer_low_confidence"


# ── Test: no-answer gate triggers on empty retrieval ───────────────────

def test_query_no_answer_empty_retrieval(client: TestClient):
    """When retrieval returns nothing, must return null answer + no citations."""
    with patch("app.main.query_chunks", return_value=[]):
        resp = client.post(
            "/query",
            json={"question": "Unrelated question?", "include_context": True},
        )

    assert resp.status_code == 200
    data = resp.json()

    assert data["answer"] is None
    assert data["citations"] == []
    assert data["retrieved_count"] == 0
    assert data["max_score"] is None
    assert data["gate_reason"] == "no_retrieval"


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
    assert data["retrieved_count"] == 1
    assert data["max_score"] == pytest.approx(0.85, rel=1e-3)
    assert data["gate_reason"] == "generated_answer"


def test_query_answerable_not_normalized_to_null(client: TestClient):
    """A normal answerable response must not be normalized into null."""
    chunks = [_make_retrieved_chunk(score=0.88)]
    from app.generation.llm import Citation, GeneratedAnswer

    gen_result = GeneratedAnswer(
        answer="Amazon Bedrock is a fully managed service [Chunk 1].",
        citations=[Citation(doc_id=chunks[0].doc_id, chunk_id=chunks[0].chunk_id)],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post("/query", json={"question": "What is Amazon Bedrock?"})

    data = resp.json()
    assert data["answer"] is not None
    assert data["citations"] != []


def test_query_no_answer_pattern_normalizes_to_null(client: TestClient):
    """No-answer phrasing from the model must map to strict null contract."""
    chunks = [_make_retrieved_chunk(score=0.40)]
    from app.generation.llm import GeneratedAnswer

    gen_result = GeneratedAnswer(
        answer="The context does not mention the default PostgreSQL version.",
        citations=[],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post(
            "/query",
            json={"question": "What is the default PostgreSQL version used internally by Bedrock?"},
        )

    data = resp.json()
    assert data["answer"] is None
    assert data["citations"] == []


def test_query_idk_high_confidence_returns_extractive_answer(client: TestClient):
    """IDK output should not become null when retrieval confidence is high."""
    chunks = [_make_retrieved_chunk(
        text="Chunking splits source documents into segments for better retrieval quality.",
        score=0.72,
    )]
    from app.generation.llm import GeneratedAnswer

    gen_result = GeneratedAnswer(
        answer="I don't know based on the provided documents.",
        citations=[],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post(
            "/query",
            json={"question": "Why are chunking settings important for answer quality?"},
        )

    data = resp.json()
    assert data["answer"] is not None
    assert data["citations"] != []


# ── Test: no "LLM unavailable" placeholder ever appears ────────────────

def test_query_no_llm_unavailable_placeholder(client: TestClient):
    """When LLM is unavailable the endpoint must return answer=None,
    never the old 'Retrieved context (LLM unavailable)' placeholder."""
    chunks = [_make_retrieved_chunk(score=0.85)]

    from app.generation.llm import GeneratedAnswer

    gen_result = GeneratedAnswer(answer=None, citations=[])

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
        patch("app.main.is_llm_available", return_value=False),
    ):
        resp = client.post("/query", json={"question": "What metrics?"})

    assert resp.status_code == 200
    data = resp.json()
    # Strict null contract: answer is None, never the placeholder
    assert data["answer"] is None
    assert data["citations"] == []


def test_query_strict_null_contract_when_llm_missing(client: TestClient):
    """Verify _fallback_answer always returns answer=None regardless of
    how many context chunks exist."""
    from app.generation.llm import _fallback_answer, GeneratedAnswer
    from app.db.chroma import RetrievedChunk

    contexts = [
        RetrievedChunk(
            chunk_id="txt/doc.txt#00000",
            doc_id="txt/doc.txt",
            text="Some relevant text about AWS Bedrock",
            score=0.9,
            source_path="/data/corpus_raw/txt/doc.txt",
            content_type="txt",
        ),
        RetrievedChunk(
            chunk_id="txt/doc2.txt#00000",
            doc_id="txt/doc2.txt",
            text="More AWS text",
            score=0.8,
            source_path="/data/corpus_raw/txt/doc2.txt",
            content_type="txt",
        ),
    ]

    result = _fallback_answer(contexts)
    assert result.answer is None
    assert result.citations == []

    # Also test with empty contexts
    result_empty = _fallback_answer([])
    assert result_empty.answer is None
    assert result_empty.citations == []


def test_query_answer_never_contains_llm_unavailable_string(client: TestClient):
    """Scan all possible answer texts — none should contain the banned
    'LLM unavailable' substring."""
    chunks = [_make_retrieved_chunk(score=0.85)]

    from app.generation.llm import GeneratedAnswer

    # Simulate normal answer
    gen_result = GeneratedAnswer(
        answer="Amazon Bedrock provides metrics [Chunk 1].",
        citations=[],
    )

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post("/query", json={"question": "What metrics?"})

    data = resp.json()
    if data["answer"] is not None:
        assert "LLM unavailable" not in data["answer"]
        assert "Retrieved context" not in data["answer"]


# ── Test: retrieval content-type balancing ─────────────────────────────

def test_retrieval_pdf_balancing():
    """When txt/md chunks exist, PDF chunks should be capped at 1."""
    from app.db.chroma import query_chunks, RetrievedChunk

    # Build fake query results: 3 PDF + 2 txt candidates
    pdf_chunks = [
        {"id": f"pdf/doc.pdf#0000{i}", "doc_id": f"pdf/doc{i}.pdf",
         "text": f"PDF content {i}", "source_path": f"/data/pdf/doc{i}.pdf",
         "content_type": "pdf"}
        for i in range(3)
    ]
    txt_chunks = [
        {"id": f"txt/doc.txt#0000{i}", "doc_id": f"txt/doc{i}.txt",
         "text": f"TXT content {i}", "source_path": f"/data/txt/doc{i}.txt",
         "content_type": "txt"}
        for i in range(2)
    ]
    all_ids = [c["id"] for c in pdf_chunks + txt_chunks]
    all_docs = [c["text"] for c in pdf_chunks + txt_chunks]
    all_metas = [
        {"doc_id": c["doc_id"], "source_path": c["source_path"],
         "content_type": c["content_type"]}
        for c in pdf_chunks + txt_chunks
    ]
    all_dists = [0.1, 0.15, 0.2, 0.25, 0.3]  # low distance = high similarity

    fake_results = {
        "ids": [all_ids],
        "documents": [all_docs],
        "metadatas": [all_metas],
        "distances": [all_dists],
    }

    with (
        patch("app.db.chroma.get_collection") as mock_coll,
    ):
        mock_coll.return_value.query.return_value = fake_results
        results = query_chunks([0.1] * 384, top_k=4, question="What metrics?")

    pdf_count = sum(1 for r in results if r.content_type == "pdf")
    assert pdf_count <= 1, f"Expected max 1 PDF chunk, got {pdf_count}"
    assert len(results) <= 4


def test_retrieval_pdf_bypass_for_iam_query():
    """For IAM/policy queries, PDF cap should NOT apply."""
    from app.db.chroma import query_chunks

    pdf_chunks = [
        {"id": f"pdf/iam.pdf#0000{i}", "doc_id": f"pdf/iam{i}.pdf",
         "text": f"IAM policy content {i}", "source_path": f"/data/pdf/iam{i}.pdf",
         "content_type": "pdf"}
        for i in range(3)
    ]
    txt_chunks = [
        {"id": "txt/doc.txt#00000", "doc_id": "txt/doc.txt",
         "text": "TXT content", "source_path": "/data/txt/doc.txt",
         "content_type": "txt"}
    ]
    all_items = pdf_chunks + txt_chunks
    fake_results = {
        "ids": [[c["id"] for c in all_items]],
        "documents": [[c["text"] for c in all_items]],
        "metadatas": [[{"doc_id": c["doc_id"], "source_path": c["source_path"],
                        "content_type": c["content_type"]} for c in all_items]],
        "distances": [[0.1, 0.15, 0.2, 0.25]],
    }

    with patch("app.db.chroma.get_collection") as mock_coll:
        mock_coll.return_value.query.return_value = fake_results
        results = query_chunks(
            [0.1] * 384, top_k=4,
            question="What IAM role policies are available?",
        )

    pdf_count = sum(1 for r in results if r.content_type == "pdf")
    # IAM query — PDF cap is bypassed, so more than 1 PDF is allowed
    assert pdf_count >= 2, f"Expected ≥2 PDF chunks for IAM query, got {pdf_count}"


def test_retrieval_definition_query_fetches_deeper():
    """Definition query should request a deeper candidate pool."""
    from app.db.chroma import query_chunks

    fake_results = {
        "ids": [["md/what-is-bedrock.html-abc#00000"]],
        "documents": [["Amazon Bedrock is a fully managed service..."]],
        "metadatas": [[{
            "doc_id": "md/what-is-bedrock.html-abc.md",
            "source_path": "/data/md/what-is-bedrock.html-abc.md",
            "content_type": "md",
        }]],
        "distances": [[0.2]],
    }

    with patch("app.db.chroma.get_collection") as mock_coll:
        mock_coll.return_value.query.return_value = fake_results
        _ = query_chunks([0.1] * 384, top_k=4, question="What is Amazon Bedrock?")

    called_kwargs = mock_coll.return_value.query.call_args.kwargs
    assert called_kwargs["n_results"] >= 50


def test_retrieval_runtime_metrics_prefers_txt_and_caps_pdf():
    """Runtime metrics queries should include txt and limit PDF to 1."""
    from app.db.chroma import query_chunks

    items = [
        {"id": "pdf/a#0", "doc_id": "pdf/a.pdf", "text": "PDF A", "source_path": "/data/pdf/a.pdf", "content_type": "pdf"},
        {"id": "pdf/b#0", "doc_id": "pdf/b.pdf", "text": "PDF B", "source_path": "/data/pdf/b.pdf", "content_type": "pdf"},
        {"id": "txt/metrics#0", "doc_id": "txt/bedrock_runtime_metrics.txt", "text": "Invocations InvocationLatency InputTokenCount OutputTokenCount", "source_path": "/data/txt/bedrock_runtime_metrics.txt", "content_type": "txt"},
        {"id": "md/c#0", "doc_id": "md/c.md", "text": "MD C", "source_path": "/data/md/c.md", "content_type": "md"},
    ]
    fake_results = {
        "ids": [[i["id"] for i in items]],
        "documents": [[i["text"] for i in items]],
        "metadatas": [[{"doc_id": i["doc_id"], "source_path": i["source_path"], "content_type": i["content_type"]} for i in items]],
        "distances": [[0.1, 0.12, 0.15, 0.2]],
    }

    with patch("app.db.chroma.get_collection") as mock_coll:
        mock_coll.return_value.query.return_value = fake_results
        results = query_chunks([0.1] * 384, top_k=4, question="What runtime metrics like InvocationLatency and Invocations are tracked?")

    assert any(r.content_type == "txt" for r in results)
    assert sum(1 for r in results if r.content_type == "pdf") <= 1


# ── Test: /health includes LLM status ──────────────────────────────────

def test_health_includes_llm_status(client: TestClient):
    """GET /health must include llm_ready and llm_reason fields."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()

    assert "llm_ready" in data
    assert "llm_reason" in data
    assert isinstance(data["llm_ready"], bool)
    assert isinstance(data["llm_reason"], str)


def test_health_llm_ready_reflects_container_state():
    """When check_llm_ready returns ready=True, /health must reflect it."""
    fake_embedding = [0.1] * 384
    with (
        patch("app.ingest.embedder.get_model"),
        patch("app.main.embed_texts", return_value=[fake_embedding]),
        patch("app.db.chroma.get_client"),
        patch("app.main.heartbeat", return_value=True),
        patch("app.main.check_llm_ready", return_value={
            "ready": True, "reason": "Groq API operational (model: test)",
        }),
    ):
        from app.main import app
        tc = TestClient(app)
        resp = tc.get("/health")

    data = resp.json()
    assert data["llm_ready"] is True
    assert "operational" in data["llm_reason"]


# ── Test: /stats endpoint ──────────────────────────────────────────────

def test_stats_endpoint(client: TestClient):
    """GET /stats must return chroma collection stats."""
    from unittest.mock import MagicMock

    mock_collection = MagicMock()
    mock_collection.count.return_value = 5
    mock_collection.get.return_value = {
        "metadatas": [
            {"content_type": "txt", "doc_id": "txt/a.txt"},
            {"content_type": "txt", "doc_id": "txt/a.txt"},
            {"content_type": "pdf", "doc_id": "pdf/b.pdf"},
            {"content_type": "pdf", "doc_id": "pdf/b.pdf"},
            {"content_type": "md", "doc_id": "md/c.md"},
        ],
    }

    with patch("app.main.get_collection", return_value=mock_collection):
        resp = client.get("/stats")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_chunks"] == 5
    assert data["by_content_type"]["txt"] == 2
    assert data["by_content_type"]["pdf"] == 2
    assert data["by_content_type"]["md"] == 1
    assert data["md_count"] == 1
    assert len(data["top_docs"]) <= 5


def test_stats_empty_collection(client: TestClient):
    """GET /stats with empty collection returns zeros."""
    from unittest.mock import MagicMock

    mock_collection = MagicMock()
    mock_collection.count.return_value = 0

    with patch("app.main.get_collection", return_value=mock_collection):
        resp = client.get("/stats")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_chunks"] == 0
    assert data["md_count"] == 0


# ── Test: "insufficient context" refusal patterns ──────────────────────

@pytest.mark.parametrize("refusal_text", [
    "insufficient context",
    "Insufficient context.",
    "insufficient information",
    "The context is insufficient to answer this question.",
    "Cannot answer based on the provided context.",
    "Unable to determine from the provided documents.",
    "No relevant information found.",
    "Not enough context to answer.",
])
def test_query_insufficient_context_normalizes_to_null(client: TestClient, refusal_text: str):
    """Various LLM refusal phrasings must all map to answer=None."""
    chunks = [_make_retrieved_chunk(score=0.40)]
    from app.generation.llm import GeneratedAnswer

    gen_result = GeneratedAnswer(answer=refusal_text, citations=[])

    with (
        patch("app.main.query_chunks", return_value=chunks),
        patch("app.main.generate_answer", return_value=gen_result),
    ):
        resp = client.post(
            "/query",
            json={"question": "What is the default PostgreSQL version?"},
        )

    data = resp.json()
    assert data["answer"] is None, f"Refusal {refusal_text!r} was not normalized to null"
    assert data["citations"] == []


def test_llm_layer_catches_insufficient_context():
    """The LLM layer's _is_unknown_answer must catch 'insufficient context'."""
    from app.generation.llm import _is_unknown_answer

    assert _is_unknown_answer("insufficient context") is True
    assert _is_unknown_answer("Insufficient context.") is True
    assert _is_unknown_answer("insufficient information") is True
    assert _is_unknown_answer("Cannot answer this question.") is True
    assert _is_unknown_answer("Unable to determine from the context.") is True
    # Real answers must NOT be caught
    assert _is_unknown_answer("Amazon Bedrock provides metrics [Chunk 1].") is False
    assert _is_unknown_answer("The context provides sufficient detail.") is False


def test_eval_runner_normalizes_refusals():
    """The eval runner's _is_refusal must normalize known refusal strings."""
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent / "scripts"))
    from run_eval import _is_refusal

    assert _is_refusal(None) is True
    assert _is_refusal("insufficient context") is True
    assert _is_refusal("Insufficient context.") is True
    assert _is_refusal("I don't know") is True
    assert _is_refusal("Cannot answer this question") is True
    # Real answers
    assert _is_refusal("Amazon Bedrock is a service.") is False
    assert _is_refusal("You can use CountTokens API.") is False
