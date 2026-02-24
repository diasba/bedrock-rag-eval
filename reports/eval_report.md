# RAG Evaluation Report

Generated: 2026-02-24 20:19:59

Dataset: 20 questions

LLM enabled (container): True — Mistral API operational (model: mistral-large-latest)

Metrics source: **judge**

### ChromaDB Collection (from API /stats)

- Total chunks: 957
- By type: md: 918, pdf: 32, txt: 7

> **Metrics mode:** Judge-backed (Mistral LLM).  Faithfulness, answer relevancy, and answer correctness were computed by an LLM judge where possible; heuristic fallback was used for any questions where the judge failed.

## Aggregate Scores

| Metric | Score |
|---|---|
| Context Precision | 0.4417 |
| Context Recall | 0.6278 |
| Faithfulness | 0.8754 |
| Answer Relevancy | 0.6042 |
| Answer Correctness | 0.7086 |

## Answerable-Only Scores

| Metric | Score |
|---|---|
| Context Precision | 0.5521 |
| Context Recall | 0.7222 |
| Faithfulness | 0.9693 |
| Answer Relevancy | 0.7552 |
| Answer Correctness | 0.6358 |

## No-Answer Contract

- No-answer questions: 4
- Correct null responses (answer=null): 4
- Hallucinated answers on no-answer rows: 0

## Scores by Category

### factual (7 questions)

- Context Precision: 0.4643
- Context Recall: 0.7143
- Faithfulness: 0.9298
- Answer Relevancy: 0.8400
- Answer Correctness: 0.6242

### multi_hop (4 questions)

- Context Precision: 0.5000
- Context Recall: 0.7500
- Faithfulness: 1.0000
- Answer Relevancy: 0.7972
- Answer Correctness: 0.7256

### no_answer (4 questions)

- Context Precision: 0.0000
- Context Recall: 0.2500
- Faithfulness: 0.5000
- Answer Relevancy: 0.0000
- Answer Correctness: 1.0000

### paraphrase (5 questions)

- Context Precision: 0.7167
- Context Recall: 0.7111
- Faithfulness: 1.0000
- Answer Relevancy: 0.6030
- Answer Correctness: 0.5803

## Per-Question Breakdown

| # | Question | Category | Ctx Prec | Ctx Rec | Faith | Ans Rel | Ans Corr |
|---|---|---|---|---|---|---|---|
| 1 | What is Amazon Bedrock? | factual | 0.00 | 0.00 | 0.80 | 0.93 | 0.46 |
| 2 | Do you need model access permissions before using … | factual | 0.58 | 1.00 | 1.00 | 0.75 | 0.70 |
| 3 | Where can you find supported models for Bedrock? | factual | 1.00 | 1.00 | 1.00 | 0.82 | 0.66 |
| 4 | What is a Bedrock Knowledge Base used for? | factual | 0.00 | 0.00 | 0.83 | 1.00 | 0.60 |
| 5 | What does chunking do in a knowledge base pipeline… | factual | 0.25 | 1.00 | 0.88 | 0.94 | 0.66 |
| 6 | What is the purpose of RetrieveAndGenerate? | factual | 0.42 | 1.00 | 1.00 | 0.68 | 0.58 |
| 7 | What is enabled by default with the correct AWS Ma… | multi_hop | 0.00 | 0.50 | 1.00 | 0.47 | 0.77 |
| 8 | In fixed-size chunking, what two settings define c… | multi_hop | 0.00 | 1.00 | 1.00 | 0.95 | 0.77 |
| 9 | In Amazon Bedrock, which feature searches your dat… | multi_hop | 1.00 | 1.00 | 1.00 | 0.91 | 0.75 |
| 10 | For Amazon Bedrock inference, which endpoint is us… | multi_hop | 1.00 | 0.50 | 1.00 | 0.86 | 0.61 |
| 11 | Can Bedrock KB do RAG-style retrieval before gener… | paraphrase | 0.58 | 0.00 | 1.00 | 0.63 | 0.61 |
| 12 | How do I check token count before sending a prompt… | paraphrase | 1.00 | 1.00 | 1.00 | 0.58 | 0.57 |
| 13 | Is there an API for streaming model responses? | paraphrase | 1.00 | 1.00 | 1.00 | 0.77 | 0.70 |
| 14 | Can I directly apply a guardrail through an API ca… | paraphrase | 1.00 | 1.00 | 1.00 | 0.66 | 0.72 |
| 15 | Name at least 5 runtime invocation metrics Bedrock… | paraphrase | 0.00 | 0.56 | 1.00 | 0.38 | 0.30 |
| 16 | In Amazon Bedrock inference, which service tier is… | factual | 1.00 | 1.00 | 1.00 | 0.75 | 0.71 |
| 17 | What is the default PostgreSQL version used intern… | no_answer | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 |
| 18 | Which color theme does the AWS Bedrock console use… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| 19 | What salary does an AWS Bedrock product manager ea… | no_answer | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 |
| 20 | What was the weather in Seattle when Bedrock launc… | no_answer | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |

## Failure Analysis

### Failure Case 1

**Question:** What is Amazon Bedrock?

**Category:** factual

**Ground Truth:** Amazon Bedrock is a fully managed service that makes foundation models from leading AI companies available through a unified API.

**Predicted:** Amazon Bedrock is a service that provides access to supported foundation models from various providers for building generative AI applications [Chunk 1]. It also offers features like Knowledge Bases, which enable Retrieval Augmented Generation (RAG) to augment model responses with information from data stores [Chunk 2].

**Average Score:** 0.4369

**Analysis:**

- Low context precision — retrieved chunks were not relevant to this question.
- Low context recall — the retrieval missed key chunks needed to answer.
- Low answer correctness — the predicted answer diverges significantly from ground truth.

### Failure Case 2

**Question:** Name at least 5 runtime invocation metrics Bedrock publishes (CloudWatch)

**Category:** paraphrase

**Ground Truth:** Amazon Bedrock tracks Invocations, InvocationLatency, InvocationClientErrors, InvocationServerErrors, InvocationThrottles, InputTokenCount, OutputTokenCount, LegacyModelInvocations, and OutputImageCount.

**Predicted:** 1. Invocations [Chunk 1]
2. InvocationLatency [Chunk 1]
3. InvocationClientErrors [Chunk 1, 3]
4. InvocationServerErrors [Chunk 3]
5. InvocationThrottles [Chunk 3]

**Average Score:** 0.4462

**Analysis:**

- Low context precision — retrieved chunks were not relevant to this question.
- Low answer relevancy — the generated answer does not address the question directly.
- Low answer correctness — the predicted answer diverges significantly from ground truth.

### Failure Case 3

**Question:** What is a Bedrock Knowledge Base used for?

**Category:** factual

**Ground Truth:** A Bedrock Knowledge Base is used to give foundation models contextual information from your private data sources for Retrieval Augmented Generation (RAG).

**Predicted:** A Bedrock Knowledge Base is used to connect to a data source and retrieve data or information when queried, enabling retrieval-augmented generation (RAG) workflows with large language models (LLMs) [Chunk 3, Chunk 4]. It allows you to define and identify a knowledge base, then query it to fetch relevant references, though guardrails are not applied to the retrieved data [Chunk 2, Chunk 3].

**Average Score:** 0.4869

**Analysis:**

- Low context precision — retrieved chunks were not relevant to this question.
- Low context recall — the retrieval missed key chunks needed to answer.

### No-Answer Behavior Summary

- True negatives (correct null): 4/4
- False positives (hallucinated answer): 0/4

## Correctness Score Distribution

- Distinct answer-correctness values (answerable rows): 0.30, 0.46, 0.57, 0.58, 0.60, 0.61, 0.66, 0.70, 0.71, 0.72, 0.75, 0.77
- Min/Median/Max: 0.3000 / 0.6583 / 0.7698

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
