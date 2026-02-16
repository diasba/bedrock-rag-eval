# RAG Evaluation Report

Generated: 2026-02-16 10:05:19

Dataset: 22 questions

LLM enabled (container): True — Mistral API operational (model: mistral-large-latest)

Metrics source: **judge**

### ChromaDB Collection (from API /stats)

- Total chunks: 953
- By type: md: 914, pdf: 32, txt: 7

> **Metrics mode:** Judge-backed (Mistral LLM).  Faithfulness, answer relevancy, and answer correctness were computed by an LLM judge where possible; heuristic fallback was used for any questions where the judge failed.

## Aggregate Scores

| Metric | Score |
|---|---|
| Context Precision | 0.4141 |
| Context Recall | 0.5530 |
| Faithfulness | 0.7561 |
| Answer Relevancy | 0.6528 |
| Answer Correctness | 0.6363 |

## Answerable-Only Scores

| Metric | Score |
|---|---|
| Context Precision | 0.5062 |
| Context Recall | 0.6759 |
| Faithfulness | 0.8685 |
| Answer Relevancy | 0.7979 |
| Answer Correctness | 0.5555 |

## No-Answer Contract

- No-answer questions: 4
- Correct null responses (answer=null): 4
- Hallucinated answers on no-answer rows: 0

## Scores by Category

### factual (8 questions)

- Context Precision: 0.6424
- Context Recall: 0.8750
- Faithfulness: 0.9375
- Answer Relevancy: 0.8661
- Answer Correctness: 0.5565

### multi_hop (4 questions)

- Context Precision: 0.1875
- Context Recall: 0.2083
- Faithfulness: 0.7000
- Answer Relevancy: 0.6874
- Answer Correctness: 0.5184

### no_answer (4 questions)

- Context Precision: 0.0000
- Context Recall: 0.0000
- Faithfulness: 0.2500
- Answer Relevancy: 0.0000
- Answer Correctness: 1.0000

### paraphrase (6 questions)

- Context Precision: 0.5371
- Context Recall: 0.7222
- Faithfulness: 0.8889
- Answer Relevancy: 0.7806
- Answer Correctness: 0.5788

## Per-Question Breakdown

| # | Question | Category | Ctx Prec | Ctx Rec | Faith | Ans Rel | Ans Corr |
|---|---|---|---|---|---|---|---|
| 1 | What is Amazon Bedrock? | factual | 1.00 | 1.00 | 1.00 | 1.00 | 0.75 |
| 2 | Do you need model access permissions before using … | factual | 0.64 | 1.00 | 1.00 | 0.89 | 0.47 |
| 3 | Where can you find supported models for Bedrock? | factual | 1.00 | 1.00 | 1.00 | 0.87 | 0.66 |
| 4 | What is a Bedrock Knowledge Base used for? | factual | 0.75 | 1.00 | 1.00 | 1.00 | 0.73 |
| 5 | What does chunking do in a knowledge base pipeline… | factual | 1.00 | 0.00 | 1.00 | 0.66 | 0.58 |
| 6 | What is the purpose of RetrieveAndGenerate? | factual | 0.75 | 1.00 | 1.00 | 0.64 | 0.57 |
| 7 | What two types of RAG evaluation jobs can you set … | factual | 0.00 | 1.00 | 0.50 | 0.86 | 0.24 |
| 8 | What does contextual grounding check in Bedrock Gu… | factual | 0.00 | 1.00 | 1.00 | 1.00 | 0.46 |
| 9 | How do model access and supported regions together… | multi_hop | 0.25 | 0.50 | 1.00 | 0.51 | 0.66 |
| 10 | Why are chunking settings and retrieval configurat… | multi_hop | 0.00 | 0.00 | 0.50 | 0.82 | 0.61 |
| 11 | How are Knowledge Bases and guardrails complementa… | multi_hop | 0.50 | 0.33 | 0.80 | 0.61 | 0.29 |
| 12 | How do quotas and endpoints influence runtime beha… | multi_hop | 0.00 | 0.00 | 0.50 | 0.80 | 0.51 |
| 13 | Can Bedrock KB do RAG-style retrieval before gener… | paraphrase | 0.81 | 1.00 | 1.00 | 0.73 | 0.70 |
| 14 | How do I check token count before sending a prompt… | paraphrase | 1.00 | 1.00 | 1.00 | 0.57 | 0.40 |
| 15 | Is there an API for streaming model responses? | paraphrase | 0.42 | 1.00 | 1.00 | 0.77 | 0.69 |
| 16 | Can I directly apply a guardrail through an API ca… | paraphrase | 1.00 | 1.00 | 1.00 | 0.79 | 0.72 |
| 17 | What are the runtime metrics Amazon Bedrock tracks… | paraphrase | 0.00 | 0.33 | 1.00 | 0.92 | 0.35 |
| 18 | Does Bedrock support tag-based access control for … | paraphrase | 0.00 | 0.00 | 0.33 | 0.90 | 0.60 |
| 19 | What is the default PostgreSQL version used intern… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| 20 | Which color theme does the AWS Bedrock console use… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| 21 | What salary does an AWS Bedrock product manager ea… | no_answer | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 |
| 22 | What was the weather in Seattle when Bedrock launc… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |

## Failure Analysis

### Failure Case 1

**Question:** How do quotas and endpoints influence runtime behavior for inference calls?

**Category:** multi_hop

**Ground Truth:** Quotas define the maximum request rate and token limits per model per region. Endpoints determine the network path for API calls. Together, exceeding quotas at a given endpoint leads to throttling (InvocationThrottles), and choosing the right endpoint-region pair is necessary to get sufficient throughput.

**Predicted:** Quotas limit the number of inference requests you can make per minute or second, and endpoints determine the regional API URL you must use for inference calls [Chunk 1].

**Average Score:** 0.3634

**Analysis:**

- Low context precision — retrieved chunks were not relevant to this question.
- Low context recall — the retrieval missed key chunks needed to answer.

### Failure Case 2

**Question:** Does Bedrock support tag-based access control for its resources?

**Category:** paraphrase

**Ground Truth:** Yes, Amazon Bedrock supports attribute-based access control (ABAC) using tags, with condition keys like aws:ResourceTag, aws:RequestTag, and aws:TagKeys.

**Predicted:** Yes, Amazon Bedrock supports tag-based access control for its resources, such as guardrails, by allowing tags to be added and referenced in policies [Chunk 2][Chunk 3].

**Average Score:** 0.3677

**Analysis:**

- Low context precision — retrieved chunks were not relevant to this question.
- Low context recall — the retrieval missed key chunks needed to answer.
- Low faithfulness — the answer contains claims not supported by retrieved context (hallucination).

### Failure Case 3

**Question:** Why are chunking settings and retrieval configuration both important for answer quality?

**Category:** multi_hop

**Ground Truth:** Chunking controls the granularity of document segments stored in the vector index, while retrieval configuration controls how many chunks are returned and how they are ranked. Together they determine whether the right information at the right level of detail reaches the LLM for generation.

**Predicted:** Chunking settings (e.g., semantic chunking, maximum tokens) improve retrieval accuracy by preserving semantic content and controlling chunk size [Chunk 2], while retrieval configuration (e.g., `numberOfResults`) determines how many relevant chunks are returned to inform the answer [Chunk 1][Chunk 3]. Together, they balance precision and context for higher-quality responses.

**Average Score:** 0.3868

**Analysis:**

- Low context precision — retrieved chunks were not relevant to this question.
- Low context recall — the retrieval missed key chunks needed to answer.

### No-Answer Behavior Summary

- True negatives (correct null): 4/4
- False positives (hallucinated answer): 0/4

## Correctness Score Distribution

- Distinct answer-correctness values (answerable rows): 0.24, 0.29, 0.35, 0.40, 0.46, 0.47, 0.51, 0.57, 0.58, 0.60, 0.61, 0.66, 0.69, 0.70, 0.72, 0.73, 0.75
- Min/Median/Max: 0.2426 / 0.6045 / 0.7522

## Metric Interpretation Notes

- **Context Recall = 1.0 with empty ground_truth_context:** When the ground-truth context field is empty, recall is trivially 1.0 because there is nothing to recall. This does NOT mean retrieval was perfect.

- **Faithfulness inflated by null answers:** A null predicted answer is counted as trivially faithful (score 1.0) because there are no claims to contradict the context. If many answers are null due to a missing LLM, Faithfulness will appear artificially high.

- **Answer Relevancy / Correctness near 0 when LLM is disabled:** Without an LLM, most answers are null, yielding 0.0 relevancy and 0.0 correctness for answerable questions. This is expected and reflects the retrieval-only baseline.

- **Why correctness looked flat (0.7/0.8):** DeepEval GEval alone can emit coarse bins. This runner now blends GEval with lexical F1 (75/25) to preserve judge behavior while improving discrimination across answerable questions.


## Suggested Improvements

### 1. Improve Chunking Strategy

The current fixed-size chunking (800 chars, 120 overlap) can split sentences mid-thought or combine unrelated sections. A semantic chunking approach — splitting on paragraph boundaries or using sentence-level segmentation — would improve context precision by ensuring each chunk is a coherent unit of information. Additionally, experimenting with smaller chunk sizes (400-500 chars) may improve retrieval precision for factual questions.

### 2. Tune Multi-Hop Retrieval (Expansion + Rerank)

The weakest category is multi-hop. Improve query decomposition, run retrieval for each sub-question, and apply an explicit cross-encoder reranker over fused candidates. This raises precision by filtering chunks that match only one side of a compositional query.
