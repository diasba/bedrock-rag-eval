#!/usr/bin/env python3
"""RAG Evaluation Runner — calls the /query API, computes metrics in two modes,
produces eval_results.json, per_question_results.csv, and eval_report.md.

Modes:
  • Default (heuristic-only): no paid API keys required.  Runs deterministic
    retrieval metrics and token-overlap heuristics.  Always succeeds.
  • Judge mode: activated automatically when GROQ_API_KEY is set.  Uses
    Groq-backed LLM judge (via LiteLLM provider prefix) for faithfulness,
    answer relevancy, and answer correctness.  Falls back to heuristics on
    any failure.

Usage:
    # heuristic-only (no keys needed)
    python scripts/run_eval.py \
        --dataset data/eval/eval_dataset.jsonl \
        --api-url http://localhost:8000

    # judge mode (Groq key present)
    GROQ_API_KEY=gsk_... python scripts/run_eval.py \
        --dataset data/eval/eval_dataset.jsonl \
        --api-url http://localhost:8000
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load repo-local .env so judge mode works without exporting env vars manually.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Prevent DeepEval from creating a .deepeval/ telemetry folder on every run.
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────

GROQ_JUDGE_MODEL = "groq/llama-3.3-70b-versatile"
"""LiteLLM-style model string used when judge mode is active."""

# ── Data structures ────────────────────────────────────────────────────


@dataclass
class EvalRecord:
    question: str
    ground_truth_answer: str | None
    ground_truth_context: str
    category: str


@dataclass
class PredictionRecord:
    question: str
    category: str
    ground_truth_answer: str | None
    ground_truth_context: str
    predicted_answer: str | None
    retrieved_contexts: list[str]
    citations: list[dict]
    retrieval_scores: list[float]


@dataclass
class QuestionResult:
    """Per-question metric scores."""
    question: str
    category: str
    predicted_answer: str | None
    ground_truth_answer: str | None
    context_precision: float | None = None
    context_recall: float | None = None
    faithfulness: float | None = None
    answer_relevancy: float | None = None
    answer_correctness: float | None = None


@dataclass
class AggregateScores:
    context_precision: float = 0.0
    context_recall: float = 0.0
    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    answer_correctness: float = 0.0


# ── Judge-mode detection ──────────────────────────────────────────────


def detect_judge_mode() -> bool:
    """Return True if a Groq API key is available for LLM-judge metrics."""
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        logger.info("GROQ_API_KEY detected — judge mode ENABLED (model: %s)", GROQ_JUDGE_MODEL)
        return True
    logger.info("No GROQ_API_KEY — running in heuristic-only mode (no paid keys required)")
    return False


# ── Step 1: Load dataset ──────────────────────────────────────────────


def load_dataset(path: str) -> list[EvalRecord]:
    records: list[EvalRecord] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            records.append(EvalRecord(
                question=obj["question"],
                ground_truth_answer=obj.get("ground_truth_answer"),
                ground_truth_context=obj.get("ground_truth_context", ""),
                category=obj.get("category", "factual"),
            ))
    logger.info("Loaded %d evaluation records", len(records))
    return records


# ── Step 2: Call API ──────────────────────────────────────────────────


def call_query_api(
    record: EvalRecord, api_url: str, client: httpx.Client,
) -> PredictionRecord:
    """Call POST /query and collect prediction."""
    resp = client.post(
        f"{api_url}/query",
        json={"question": record.question, "include_context": True},
        timeout=120.0,
    )
    resp.raise_for_status()
    data = resp.json()

    retrieved = data.get("retrieved") or []
    contexts = [r["text"] for r in retrieved]
    scores = [r["score"] for r in retrieved]
    citations = data.get("citations") or []

    return PredictionRecord(
        question=record.question,
        category=record.category,
        ground_truth_answer=record.ground_truth_answer,
        ground_truth_context=record.ground_truth_context,
        predicted_answer=data.get("answer"),
        retrieved_contexts=contexts,
        citations=citations,
        retrieval_scores=scores,
    )


def collect_predictions(
    records: list[EvalRecord], api_url: str,
) -> list[PredictionRecord]:
    predictions: list[PredictionRecord] = []
    with httpx.Client() as client:
        for i, rec in enumerate(records, 1):
            logger.info("[%d/%d] Querying: %s", i, len(records), rec.question[:60])
            try:
                pred = call_query_api(rec, api_url, client)
                predictions.append(pred)
            except Exception as exc:
                logger.warning("Failed for question %d: %s", i, exc)
                predictions.append(PredictionRecord(
                    question=rec.question,
                    category=rec.category,
                    ground_truth_answer=rec.ground_truth_answer,
                    ground_truth_context=rec.ground_truth_context,
                    predicted_answer=None,
                    retrieved_contexts=[],
                    citations=[],
                    retrieval_scores=[],
                ))
            # Small delay to avoid rate-limiting Groq
            time.sleep(1.5)
    return predictions


# ── Step 2c: Normalize refusal strings to None ──────────────────────

_REFUSAL_PATTERNS = [
    re.compile(r"^insufficient (context|information)\.?$", re.IGNORECASE),
    re.compile(r"^i don't know", re.IGNORECASE),
    re.compile(r"^i do not know", re.IGNORECASE),
    re.compile(r"^not enough (information|context)", re.IGNORECASE),
    re.compile(r"^no relevant (information|context)", re.IGNORECASE),
    re.compile(r"^(cannot|can't|unable to) (answer|determine)", re.IGNORECASE),
    re.compile(r"^the (provided )?context (is )?(insufficient|does not)", re.IGNORECASE),
    re.compile(r"^based on the (provided )?(context|documents?).{0,15}(cannot|can't|don't)", re.IGNORECASE),
]


def _is_refusal(answer: str | None) -> bool:
    """Return True if the answer is a known LLM refusal/no-answer string."""
    if answer is None:
        return True
    text = answer.strip()
    if not text:
        return True
    return any(p.search(text) for p in _REFUSAL_PATTERNS)


def _normalize_predictions(predictions: list[PredictionRecord]) -> list[PredictionRecord]:
    """Replace known refusal strings with None so scoring treats them as no-answer."""
    normalized = 0
    for p in predictions:
        if p.predicted_answer is not None and _is_refusal(p.predicted_answer):
            logger.info("Normalizing refusal to null: %r", p.predicted_answer)
            p.predicted_answer = None
            normalized += 1
    if normalized:
        logger.info("Normalized %d refusal answers to null", normalized)
    return predictions


# ── Step 3: Compute metrics ──────────────────────────────────────────
# ── 3a. Heuristic (deterministic) metrics — always available ─────────


def _heuristic_context_precision(
    retrieved_contexts: list[str], ground_truth_context: str,
) -> float:
    """Fraction of retrieved chunks that overlap meaningfully with the
    ground-truth context (token-Jaccard > 0.1 counts as relevant)."""
    if not retrieved_contexts or not ground_truth_context:
        return 0.0
    gt_tokens = set(ground_truth_context.lower().split())
    if not gt_tokens:
        return 0.0
    relevant = 0
    for ctx in retrieved_contexts:
        ctx_tokens = set(ctx.lower().split())
        if not ctx_tokens:
            continue
        jaccard = len(ctx_tokens & gt_tokens) / len(ctx_tokens | gt_tokens)
        if jaccard > 0.1:
            relevant += 1
    return relevant / len(retrieved_contexts)


def _heuristic_context_recall(
    retrieved_contexts: list[str], ground_truth_context: str,
) -> float:
    """Token-recall of the ground-truth context covered by the union of
    all retrieved chunks."""
    if not ground_truth_context:
        return 1.0  # no expected context — trivially satisfied
    gt_tokens = set(ground_truth_context.lower().split())
    if not gt_tokens:
        return 1.0
    covered: set[str] = set()
    for ctx in retrieved_contexts:
        covered |= set(ctx.lower().split())
    return len(gt_tokens & covered) / len(gt_tokens)


def _heuristic_faithfulness(
    predicted_answer: str | None, retrieved_contexts: list[str],
) -> float:
    """Token-precision: fraction of answer tokens that appear somewhere in
    the retrieved contexts (proxy for groundedness)."""
    if not predicted_answer:
        return 1.0  # null answer is trivially faithful
    ans_tokens = set(predicted_answer.lower().split())
    # Remove very common stop-words to reduce noise
    stop = {"the", "a", "an", "is", "are", "was", "were", "of", "in", "to",
            "and", "for", "on", "with", "that", "it", "this", "by", "as", "or",
            "be", "from", "at", "not", "but", "its", "can", "you", "your"}
    ans_tokens -= stop
    if not ans_tokens:
        return 1.0
    ctx_tokens: set[str] = set()
    for ctx in retrieved_contexts:
        ctx_tokens |= set(ctx.lower().split())
    return len(ans_tokens & ctx_tokens) / len(ans_tokens)


def _heuristic_answer_relevancy(
    question: str, predicted_answer: str | None,
) -> float:
    """Token-overlap between question and answer as a rough relevancy proxy."""
    if not predicted_answer:
        return 0.0
    q_tokens = set(question.lower().split())
    a_tokens = set(predicted_answer.lower().split())
    stop = {"the", "a", "an", "is", "are", "was", "were", "of", "in", "to",
            "and", "for", "on", "with", "what", "how", "does", "do", "which",
            "can", "?", "be", "that", "this"}
    q_tokens -= stop
    a_tokens -= stop
    if not q_tokens:
        return 1.0
    return len(q_tokens & a_tokens) / len(q_tokens)


def _heuristic_correctness(predicted: str | None, ground_truth: str) -> float:
    """Simple token-overlap F1 as a fallback correctness metric."""
    if not predicted:
        return 0.0
    pred_tokens = set(predicted.lower().split())
    gt_tokens = set(ground_truth.lower().split())
    if not gt_tokens:
        return 0.0
    overlap = pred_tokens & gt_tokens
    if not overlap:
        return 0.0
    precision = len(overlap) / len(pred_tokens)
    recall = len(overlap) / len(gt_tokens)
    return round(2 * precision * recall / (precision + recall), 4)


def compute_heuristic_metrics(
    predictions: list[PredictionRecord],
) -> list[QuestionResult]:
    """Compute all five metrics using fast, deterministic heuristics.
    Never fails, never requires external API keys."""
    logger.info("Computing heuristic metrics for %d predictions...", len(predictions))
    results: list[QuestionResult] = []
    for p in predictions:
        ctx_prec = _heuristic_context_precision(
            p.retrieved_contexts, p.ground_truth_context,
        )
        ctx_rec = _heuristic_context_recall(
            p.retrieved_contexts, p.ground_truth_context,
        )
        faith = _heuristic_faithfulness(p.predicted_answer, p.retrieved_contexts)
        ans_rel = _heuristic_answer_relevancy(p.question, p.predicted_answer)

        if p.ground_truth_answer is None:
            ans_corr = 1.0 if p.predicted_answer is None else 0.0
        else:
            ans_corr = _heuristic_correctness(p.predicted_answer, p.ground_truth_answer)

        results.append(QuestionResult(
            question=p.question,
            category=p.category,
            predicted_answer=p.predicted_answer,
            ground_truth_answer=p.ground_truth_answer,
            context_precision=round(ctx_prec, 4),
            context_recall=round(ctx_rec, 4),
            faithfulness=round(faith, 4),
            answer_relevancy=round(ans_rel, 4),
            answer_correctness=round(ans_corr, 4),
        ))
    logger.info("Heuristic metrics complete")
    return results


# ── 3b. Judge-backed metrics (RAGAS + DeepEval via Groq) ─────────────


def _try_ragas_judge(
    predictions: list[PredictionRecord],
    results: list[QuestionResult],
) -> tuple[list[QuestionResult], bool]:
    """Attempt RAGAS judge metrics using Groq via langchain-groq.
    On ANY failure, logs a warning and returns results untouched.
    Returns (results, actually_applied)."""
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
        from langchain_groq import ChatGroq
    except ImportError as exc:
        logger.warning("RAGAS/langchain-groq not installed — skipping judge metrics: %s", exc)
        return results, False

    try:
        # Configure LLM wrapper for RAGAS using Groq
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.environ["GROQ_API_KEY"],
            temperature=0.0,
        )

        ragas_data = {
            "question": [],
            "answer": [],
            "contexts": [],
            "ground_truth": [],
        }
        for p in predictions:
            ragas_data["question"].append(p.question)
            ragas_data["answer"].append(p.predicted_answer or "I don't know.")
            ragas_data["contexts"].append(
                p.retrieved_contexts if p.retrieved_contexts else ["No context retrieved."],
            )
            ragas_data["ground_truth"].append(
                p.ground_truth_answer or "This question has no answer in the corpus.",
            )

        dataset = Dataset.from_dict(ragas_data)
        logger.info("Running RAGAS judge evaluation on %d samples (Groq-backed)...", len(predictions))

        result = evaluate(
            dataset=dataset,
            metrics=[context_precision, context_recall, faithfulness, answer_relevancy],
            llm=llm,
        )

        result_df = result.to_pandas()
        for i in range(len(predictions)):
            cp = _safe_float(result_df.iloc[i].get("context_precision"))
            cr = _safe_float(result_df.iloc[i].get("context_recall"))
            fa = _safe_float(result_df.iloc[i].get("faithfulness"))
            ar = _safe_float(result_df.iloc[i].get("answer_relevancy"))
            if cp is not None:
                results[i].context_precision = cp
            if cr is not None:
                results[i].context_recall = cr
            if fa is not None:
                results[i].faithfulness = fa
            if ar is not None:
                results[i].answer_relevancy = ar

        logger.info("RAGAS judge metrics applied successfully")
        return results, True

    except Exception as exc:
        logger.warning("RAGAS judge evaluation failed — keeping heuristic scores: %s", exc)
        return results, False


def _try_deepeval_judge(
    predictions: list[PredictionRecord],
    results: list[QuestionResult],
) -> tuple[list[QuestionResult], bool]:
    """Attempt DeepEval GEval correctness using Groq via LiteLLM.
    On ANY failure, logs a warning and returns results untouched.
    Returns (results, actually_applied)."""
    try:
        from deepeval.metrics import GEval
        from deepeval.test_case import LLMTestCase, LLMTestCaseParams
    except ImportError as exc:
        logger.warning("DeepEval not installed — skipping judge correctness: %s", exc)
        return results, False

    try:
        # Tell DeepEval to use the Groq model via LiteLLM
        metric = GEval(
            name="Answer Correctness",
            criteria="Determine whether the actual output is factually correct based on the expected output.",
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            threshold=0.5,
            model=GROQ_JUDGE_MODEL,
        )

        logger.info("Running DeepEval GEval correctness on %d samples (Groq-backed)...", len(predictions))

        for i, p in enumerate(predictions):
            if p.ground_truth_answer is None:
                # No-answer: keep existing heuristic score
                continue
            try:
                test_case = LLMTestCase(
                    input=p.question,
                    actual_output=p.predicted_answer or "I don't know.",
                    expected_output=p.ground_truth_answer,
                )
                metric.measure(test_case)
                if metric.score is not None:
                    results[i].answer_correctness = round(metric.score, 4)
            except Exception as exc:
                logger.warning(
                    "DeepEval GEval failed for q%d — keeping heuristic: %s", i + 1, exc,
                )

        logger.info("DeepEval judge correctness applied successfully")

    except Exception as exc:
        logger.warning("DeepEval judge init failed — keeping heuristic scores: %s", exc)
        return results, False

    return results, True


def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        f = float(val)
        return None if math.isnan(f) else round(f, 4)
    except (ValueError, TypeError):
        return None


# ── Step 4: Aggregate ────────────────────────────────────────────────


def aggregate_scores(results: list[QuestionResult]) -> AggregateScores:
    """Compute mean of each metric across all questions (ignoring None)."""
    def _mean(vals: list[float | None]) -> float:
        valid = [v for v in vals if v is not None]
        return round(sum(valid) / len(valid), 4) if valid else 0.0

    return AggregateScores(
        context_precision=_mean([r.context_precision for r in results]),
        context_recall=_mean([r.context_recall for r in results]),
        faithfulness=_mean([r.faithfulness for r in results]),
        answer_relevancy=_mean([r.answer_relevancy for r in results]),
        answer_correctness=_mean([r.answer_correctness for r in results]),
    )


# ── Step 5: Output artifacts ─────────────────────────────────────────


def save_json(
    results: list[QuestionResult],
    agg: AggregateScores,
    out_dir: Path,
    *,
    judge_mode: bool,
    llm_enabled: bool = False,
    llm_status: str = "",
    chroma_stats: dict | None = None,
    metrics_source: str = "heuristic",
) -> None:
    out = {
        "judge_mode": judge_mode,
        "llm_enabled": llm_enabled,
        "llm_status": llm_status,
        "metrics_source": metrics_source,
        "chroma_stats": chroma_stats or {},
        "aggregate": asdict(agg),
        "per_question": [asdict(r) for r in results],
    }
    path = out_dir / "eval_results.json"
    path.write_text(json.dumps(out, indent=2, default=str))
    logger.info("Saved %s", path)


def save_csv(results: list[QuestionResult], out_dir: Path) -> None:
    path = out_dir / "per_question_results.csv"
    fields = [
        "question", "category", "predicted_answer", "ground_truth_answer",
        "context_precision", "context_recall", "faithfulness",
        "answer_relevancy", "answer_correctness",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))
    logger.info("Saved %s", path)


def generate_report(
    results: list[QuestionResult],
    agg: AggregateScores,
    predictions: list[PredictionRecord],
    out_dir: Path,
    *,
    judge_mode: bool,
    llm_enabled: bool = False,
    llm_status: str = "",
    chroma_stats: dict | None = None,
    metrics_source: str = "heuristic",
) -> None:
    """Generate eval_report.md with aggregate scores, per-question breakdown,
    failure analysis, and improvement suggestions."""

    lines: list[str] = []
    lines.append("# RAG Evaluation Report\n")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"Dataset: {len(results)} questions\n")
    lines.append(f"LLM enabled (container): {llm_enabled} — {llm_status}\n")
    lines.append(f"Metrics source: **{metrics_source}**\n")

    # ── Chroma stats summary ──────────────────────────────────────────
    if chroma_stats:
        lines.append("### ChromaDB Collection (from API /stats)\n")
        lines.append(f"- Total chunks: {chroma_stats.get('total_chunks', 0)}")
        by_ct = chroma_stats.get('by_content_type', {})
        if by_ct:
            ct_parts = ", ".join(f"{k}: {v}" for k, v in sorted(by_ct.items()))
            lines.append(f"- By type: {ct_parts}")
        lines.append("")

    # ── Mode banner ───────────────────────────────────────────────────
    if metrics_source == "judge":
        lines.append(
            "> **Metrics mode:** Judge-backed (Groq LLM via LiteLLM).  "
            "Faithfulness, answer relevancy, and answer correctness were "
            "computed by an LLM judge where possible; heuristic fallback "
            "was used for any questions where the judge failed.\n"
        )
    elif metrics_source == "mixed":
        lines.append(
            "> **Metrics mode:** Mixed — some judge metrics applied, "
            "others fell back to heuristic.  Check logs for details "
            "on which judge frameworks succeeded.\n"
        )
    else:
        banner_reason = ""
        if judge_mode and not llm_enabled:
            banner_reason = (
                "  GROQ_API_KEY is set on the host, but the API container "
                "reported LLM not ready — judge metrics were skipped."
            )
        elif judge_mode:
            banner_reason = (
                "  Judge mode was requested but judge frameworks "
                "(langchain-groq / deepeval) failed or are not installed "
                "on the host — all scores are heuristic fallback."
            )
        lines.append(
            "> **Metrics mode:** Heuristic-only.  "
            "All scores are based on deterministic token-overlap heuristics."
            f"{banner_reason}\n"
        )

    # ── Aggregate scores ──────────────────────────────────────────────
    lines.append("## Aggregate Scores\n")
    lines.append("| Metric | Score |")
    lines.append("|---|---|")
    lines.append(f"| Context Precision | {agg.context_precision:.4f} |")
    lines.append(f"| Context Recall | {agg.context_recall:.4f} |")
    lines.append(f"| Faithfulness | {agg.faithfulness:.4f} |")
    lines.append(f"| Answer Relevancy | {agg.answer_relevancy:.4f} |")
    lines.append(f"| Answer Correctness | {agg.answer_correctness:.4f} |")
    lines.append("")

    # ── Per-category breakdown ────────────────────────────────────────
    lines.append("## Scores by Category\n")
    categories = sorted(set(r.category for r in results))
    for cat in categories:
        cat_results = [r for r in results if r.category == cat]
        cat_agg = aggregate_scores(cat_results)
        lines.append(f"### {cat} ({len(cat_results)} questions)\n")
        lines.append(f"- Context Precision: {cat_agg.context_precision:.4f}")
        lines.append(f"- Context Recall: {cat_agg.context_recall:.4f}")
        lines.append(f"- Faithfulness: {cat_agg.faithfulness:.4f}")
        lines.append(f"- Answer Relevancy: {cat_agg.answer_relevancy:.4f}")
        lines.append(f"- Answer Correctness: {cat_agg.answer_correctness:.4f}")
        lines.append("")

    # ── Per-question breakdown ────────────────────────────────────────
    lines.append("## Per-Question Breakdown\n")
    lines.append("| # | Question | Category | Ctx Prec | Ctx Rec | Faith | Ans Rel | Ans Corr |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(results, 1):
        def _fmt(v):
            return f"{v:.2f}" if v is not None else "\u2014"
        q_short = r.question[:50] + ("\u2026" if len(r.question) > 50 else "")
        lines.append(
            f"| {i} | {q_short} | {r.category} | "
            f"{_fmt(r.context_precision)} | {_fmt(r.context_recall)} | "
            f"{_fmt(r.faithfulness)} | {_fmt(r.answer_relevancy)} | "
            f"{_fmt(r.answer_correctness)} |"
        )
    lines.append("")

    # ── Failure analysis ──────────────────────────────────────────────
    lines.append("## Failure Analysis\n")

    # Find worst performers by lowest average across available metrics
    scored: list[tuple[int, float, QuestionResult, PredictionRecord]] = []
    for i, (r, p) in enumerate(zip(results, predictions)):
        vals = [
            v for v in [
                r.context_precision, r.context_recall,
                r.faithfulness, r.answer_relevancy, r.answer_correctness,
            ] if v is not None
        ]
        avg = sum(vals) / len(vals) if vals else 0.0
        scored.append((i, avg, r, p))

    scored.sort(key=lambda x: x[1])
    failures = scored[:3]

    for rank, (idx, avg_score, r, p) in enumerate(failures, 1):
        lines.append(f"### Failure Case {rank}\n")
        lines.append(f"**Question:** {r.question}\n")
        lines.append(f"**Category:** {r.category}\n")
        lines.append(f"**Ground Truth:** {r.ground_truth_answer}\n")
        lines.append(f"**Predicted:** {r.predicted_answer}\n")
        lines.append(f"**Average Score:** {avg_score:.4f}\n")

        # Analyze why it failed
        issues: list[str] = []
        if r.context_precision is not None and r.context_precision < 0.5:
            issues.append("Low context precision \u2014 retrieved chunks were not relevant to this question.")
        if r.context_recall is not None and r.context_recall < 0.5:
            issues.append("Low context recall \u2014 the retrieval missed key chunks needed to answer.")
        if r.faithfulness is not None and r.faithfulness < 0.5:
            issues.append("Low faithfulness \u2014 the answer contains claims not supported by retrieved context (hallucination).")
        if r.answer_relevancy is not None and r.answer_relevancy < 0.5:
            issues.append("Low answer relevancy \u2014 the generated answer does not address the question directly.")
        if r.answer_correctness is not None and r.answer_correctness < 0.5:
            issues.append("Low answer correctness \u2014 the predicted answer diverges significantly from ground truth.")
        if p.predicted_answer is None and r.ground_truth_answer is not None:
            issues.append("Pipeline returned null answer for a question that has an answer in the corpus.")
        if p.predicted_answer is not None and r.ground_truth_answer is None:
            issues.append("Pipeline returned an answer for a no-answer question (hallucination).")
        if not p.retrieved_contexts:
            issues.append("No contexts were retrieved \u2014 embedding similarity was too low.")

        if issues:
            lines.append("**Analysis:**\n")
            for issue in issues:
                lines.append(f"- {issue}")
        else:
            lines.append("**Analysis:**\n")
            lines.append("- Score is low across multiple metrics \u2014 likely a combination of retrieval and generation issues.")

        lines.append("")

    # ── Metric artifact explanations ──────────────────────────────────
    lines.append("## Metric Interpretation Notes\n")
    lines.append(
        "- **Context Recall = 1.0 with empty ground_truth_context:** "
        "When the ground-truth context field is empty, recall is trivially "
        "1.0 because there is nothing to recall. This does NOT mean "
        "retrieval was perfect.\n"
    )
    lines.append(
        "- **Faithfulness inflated by null answers:** "
        "A null predicted answer is counted as trivially faithful "
        "(score 1.0) because there are no claims to contradict the context. "
        "If many answers are null due to a missing LLM, Faithfulness will "
        "appear artificially high.\n"
    )
    lines.append(
        "- **Answer Relevancy / Correctness near 0 when LLM is disabled:** "
        "Without an LLM, most answers are null, yielding 0.0 relevancy "
        "and 0.0 correctness for answerable questions. This is expected "
        "and reflects the retrieval-only baseline.\n"
    )
    if not llm_enabled:
        lines.append(
            "> ⚠️  **LLM was disabled for this run.** Judge metrics were "
            "skipped. Set `GROQ_API_KEY` and re-run to get full evaluation.\n"
        )
    lines.append("")

    # ── Improvement suggestions ───────────────────────────────────────
    lines.append("## Suggested Improvements\n")
    lines.append("### 1. Improve Chunking Strategy\n")
    lines.append(
        "The current fixed-size chunking (800 chars, 120 overlap) can split "
        "sentences mid-thought or combine unrelated sections. A semantic chunking "
        "approach \u2014 splitting on paragraph boundaries or using sentence-level "
        "segmentation \u2014 would improve context precision by ensuring each chunk "
        "is a coherent unit of information. Additionally, experimenting with "
        "smaller chunk sizes (400-500 chars) may improve retrieval precision "
        "for factual questions.\n"
    )
    lines.append("### 2. Add Hybrid Retrieval (BM25 + Vector)\n")
    lines.append(
        "Pure vector search can miss keyword-specific matches (e.g., exact "
        "metric names, API operation names). Adding a BM25 sparse retrieval "
        "layer and combining scores with reciprocal rank fusion would improve "
        "context recall, especially for factual and paraphrase questions that "
        "rely on specific terminology. ChromaDB supports metadata filtering "
        "which could also help with targeted retrieval.\n"
    )

    if metrics_source == "heuristic":
        lines.append("### 3. Enable Judge Metrics\n")
        lines.append(
            "This report was generated with heuristic-only metrics. "
            "Ensure `langchain-groq` and `deepeval` are installed on the "
            "host running `run_eval.py`, set `GROQ_API_KEY`, and verify "
            "the API container also has `GROQ_API_KEY` so the LLM can "
            "generate real answers.\n"
        )

    # Write report
    path = out_dir / "eval_report.md"
    path.write_text("\n".join(lines))
    logger.info("Saved %s", path)


# ── Main ──────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAG evaluation")
    parser.add_argument(
        "--dataset", required=True,
        help="Path to eval dataset JSONL file",
    )
    parser.add_argument(
        "--api-url", default="http://localhost:8000",
        help="Base URL of the RAG API",
    )
    parser.add_argument(
        "--output-dir", default="reports",
        help="Directory for output artifacts",
    )
    parser.add_argument(
        "--require-llm", action="store_true", default=False,
        help="Fail fast if the Groq LLM is not operational",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    api_url = args.api_url

    # ── 0a. Preflight: check API is up ───────────────────────────────
    logger.info("Preflight: checking API at %s ...", api_url)
    try:
        with httpx.Client() as hc:
            health_resp = hc.get(f"{api_url}/health", timeout=10.0)
            health_resp.raise_for_status()
            health_data = health_resp.json()
    except Exception as exc:
        logger.error("Cannot reach API at %s: %s", api_url, exc)
        sys.exit(1)

    # LLM readiness — from the CONTAINER, not the host
    llm_enabled: bool = health_data.get("llm_ready", False)
    llm_status: str = health_data.get("llm_reason", "unknown")
    logger.info("Container LLM ready: %s — %s", llm_enabled, llm_status)

    if args.require_llm and not llm_enabled:
        logger.error("--require-llm set but container LLM is NOT ready: %s", llm_status)
        sys.exit(1)

    # ── 0b. Chroma stats — from the CONTAINER via /stats ─────────────
    chroma_stats: dict = {}
    try:
        with httpx.Client() as hc:
            stats_resp = hc.get(f"{api_url}/stats", timeout=15.0)
            stats_resp.raise_for_status()
            chroma_stats = stats_resp.json()
        logger.info("Chroma stats (from API): %s", json.dumps(chroma_stats))

        total_chunks = chroma_stats.get("total_chunks", 0)
        md_count = chroma_stats.get("md_count", 0)

        if total_chunks == 0:
            logger.error("⚠️  ChromaDB has 0 chunks — did you forget to POST /ingest?")
        if md_count == 0:
            logger.warning("⚠️  No markdown chunks found — md_count == 0. "
                           "Consider ingesting .md files for better coverage.")
        if 0 < total_chunks < 50:
            logger.warning("⚠️  Only %d chunks in ChromaDB (< 50). "
                           "Evaluation may not be representative.", total_chunks)
    except Exception as exc:
        logger.warning("Could not fetch /stats from API: %s", exc)

    # ── 0c. Detect judge mode ────────────────────────────────────────
    #  Judge mode requires BOTH:
    #    1. GROQ_API_KEY on the host (for RAGAS / DeepEval to call Groq)
    #    2. Container LLM ready (so /query returns real answers to evaluate)
    host_groq_key = detect_judge_mode()
    judge_mode = host_groq_key and llm_enabled
    if host_groq_key and not llm_enabled:
        logger.warning("GROQ_API_KEY is set on host, but container LLM is NOT ready — "
                       "judge metrics will be SKIPPED (no real answers to judge)")

    # 1. Load dataset
    records = load_dataset(args.dataset)

    # 2. Collect predictions from API
    predictions = collect_predictions(records, api_url)

    # ── 2a. Normalize refusal strings ("insufficient context" etc.) to null
    predictions = _normalize_predictions(predictions)

    # ── 2b. Sanity check: how many answers are null? ─────────────────
    null_count = sum(1 for p in predictions if p.predicted_answer is None)
    answerable = sum(1 for p in predictions if p.ground_truth_answer is not None)
    null_answerable = sum(
        1 for p in predictions
        if p.predicted_answer is None and p.ground_truth_answer is not None
    )
    logger.info(
        "Predictions: %d total, %d null answers, %d/%d answerable returned null",
        len(predictions), null_count, null_answerable, answerable,
    )
    if null_answerable == answerable and answerable > 0:
        logger.warning(
            "⚠️  ALL %d answerable questions returned null. "
            "The container likely cannot generate LLM answers. "
            "Check: container GROQ_API_KEY, retrieval scores, no-answer threshold.",
            answerable,
        )

    # 3. Always compute heuristic baseline (never fails)
    results = compute_heuristic_metrics(predictions)

    # 4. If judge mode, attempt to upgrade — TRACK whether it worked
    ragas_applied = False
    deepeval_applied = False
    if judge_mode:
        results, ragas_applied = _try_ragas_judge(predictions, results)
        results, deepeval_applied = _try_deepeval_judge(predictions, results)

    # Determine actual metrics source
    if ragas_applied and deepeval_applied:
        metrics_source = "judge"
    elif ragas_applied or deepeval_applied:
        metrics_source = "mixed"
    else:
        metrics_source = "heuristic"

    if judge_mode and metrics_source == "heuristic":
        logger.warning(
            "⚠️  Judge mode was enabled but ALL judge frameworks failed. "
            "Report will say heuristic-only. Check that langchain-groq "
            "and deepeval are installed on the HOST."
        )

    logger.info("Metrics source: %s (ragas=%s, deepeval=%s)",
                metrics_source, ragas_applied, deepeval_applied)

    # 5. Aggregate
    agg = aggregate_scores(results)
    logger.info("Aggregate scores: %s", asdict(agg))

    # 6. Save outputs (always succeeds — all 3 artifacts)
    save_json(
        results, agg, out_dir,
        judge_mode=judge_mode,
        llm_enabled=llm_enabled,
        llm_status=llm_status,
        chroma_stats=chroma_stats,
        metrics_source=metrics_source,
    )
    save_csv(results, out_dir)
    generate_report(
        results, agg, predictions, out_dir,
        judge_mode=judge_mode,
        llm_enabled=llm_enabled,
        llm_status=llm_status,
        chroma_stats=chroma_stats,
        metrics_source=metrics_source,
    )

    logger.info("Evaluation complete. Artifacts in %s/", out_dir)


if __name__ == "__main__":
    main()
