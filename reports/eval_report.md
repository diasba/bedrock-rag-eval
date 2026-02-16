# RAG Evaluation Report

Generated: 2026-02-16 16:31:17

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
| Context Precision | 0.6319 |
| Context Recall | 0.6528 |
| Faithfulness | 0.8500 |
| Answer Relevancy | 0.6184 |
| Answer Correctness | 0.7037 |

## Answerable-Only Scores

| Metric | Score |
|---|---|
| Context Precision | 0.7899 |
| Context Recall | 0.8160 |
| Faithfulness | 1.0000 |
| Answer Relevancy | 0.7730 |
| Answer Correctness | 0.6296 |

## No-Answer Contract

- No-answer questions: 4
- Correct null responses (answer=null): 4
- Hallucinated answers on no-answer rows: 0

## Scores by Category

### factual (7 questions)

- Context Precision: 0.7698
- Context Recall: 1.0000
- Faithfulness: 1.0000
- Answer Relevancy: 0.8852
- Answer Correctness: 0.6699

### multi_hop (4 questions)

- Context Precision: 0.8750
- Context Recall: 0.6250
- Faithfulness: 1.0000
- Answer Relevancy: 0.7640
- Answer Correctness: 0.6196

### no_answer (4 questions)

- Context Precision: 0.0000
- Context Recall: 0.0000
- Faithfulness: 0.2500
- Answer Relevancy: 0.0000
- Answer Correctness: 1.0000

### paraphrase (5 questions)

- Context Precision: 0.7500
- Context Recall: 0.7111
- Faithfulness: 1.0000
- Answer Relevancy: 0.6230
- Answer Correctness: 0.5812

## Per-Question Breakdown

| # | Question | Category | Ctx Prec | Ctx Rec | Faith | Ans Rel | Ans Corr |
|---|---|---|---|---|---|---|---|
| 1 | What is Amazon Bedrock? | factual | 1.00 | 1.00 | 1.00 | 1.00 | 0.74 |
| 2 | Do you need model access permissions before using … | factual | 0.81 | 1.00 | 1.00 | 1.00 | 0.69 |
| 3 | Where can you find supported models for Bedrock? | factual | 1.00 | 1.00 | 1.00 | 0.82 | 0.64 |
| 4 | What is a Bedrock Knowledge Base used for? | factual | 0.50 | 1.00 | 1.00 | 0.81 | 0.67 |
| 5 | What does chunking do in a knowledge base pipeline… | factual | 0.75 | 1.00 | 1.00 | 0.98 | 0.63 |
| 6 | What is the purpose of RetrieveAndGenerate? | factual | 0.83 | 1.00 | 1.00 | 0.79 | 0.60 |
| 7 | What is enabled by default with the correct AWS Ma… | multi_hop | 1.00 | 0.50 | 1.00 | 0.47 | 0.77 |
| 8 | In fixed-size chunking, what two settings define c… | multi_hop | 0.50 | 1.00 | 1.00 | 0.91 | 0.84 |
| 9 | In Amazon Bedrock, which feature searches your dat… | multi_hop | 1.00 | 0.50 | 1.00 | 0.78 | 0.35 |
| 10 | For Amazon Bedrock inference, which endpoint is us… | multi_hop | 1.00 | 0.50 | 1.00 | 0.89 | 0.52 |
| 11 | Can Bedrock KB do RAG-style retrieval before gener… | paraphrase | 0.75 | 0.00 | 1.00 | 0.72 | 0.70 |
| 12 | How do I check token count before sending a prompt… | paraphrase | 1.00 | 1.00 | 1.00 | 0.65 | 0.65 |
| 13 | Is there an API for streaming model responses? | paraphrase | 1.00 | 1.00 | 1.00 | 0.77 | 0.65 |
| 14 | Can I directly apply a guardrail through an API ca… | paraphrase | 1.00 | 1.00 | 1.00 | 0.66 | 0.61 |
| 15 | Name at least 5 runtime invocation metrics Bedrock… | paraphrase | 0.00 | 0.56 | 1.00 | 0.32 | 0.30 |
| 16 | In Amazon Bedrock inference, which service tier is… | factual | 0.50 | 1.00 | 1.00 | 0.79 | 0.71 |
| 17 | What is the default PostgreSQL version used intern… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| 18 | Which color theme does the AWS Bedrock console use… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| 19 | What salary does an AWS Bedrock product manager ea… | no_answer | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 |
| 20 | What was the weather in Seattle when Bedrock launc… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |

## Failure Analysis

### Failure Case 1

**Question:** Name at least 5 runtime invocation metrics Bedrock publishes (CloudWatch)

**Category:** paraphrase

**Ground Truth:** Amazon Bedrock tracks Invocations, InvocationLatency, InvocationClientErrors, InvocationServerErrors, InvocationThrottles, InputTokenCount, OutputTokenCount, LegacyModelInvocations, and OutputImageCount.

**Predicted:** 1. Invocations [Chunk 1]
2. InvocationLatency [Chunk 1]
3. InvocationClientErrors [Chunk 1, 3]
4. InvocationServerErrors [Chunk 3]
5. InvocationThrottles [Chunk 3]

**Average Score:** 0.4353

**Analysis:**

- Low context precision — retrieved chunks were not relevant to this question.
- Low answer relevancy — the generated answer does not address the question directly.
- Low answer correctness — the predicted answer diverges significantly from ground truth.

### Failure Case 2

**Question:** Can Bedrock KB do RAG-style retrieval before generation?

**Category:** paraphrase

**Ground Truth:** Yes, Bedrock Knowledge Bases support RAG-style retrieval before generation through the RetrieveAndGenerate API, which first queries the knowledge base for relevant results and then uses them to augment the prompt for the foundation model.

**Predicted:** Yes, Amazon Bedrock Knowledge Bases can perform RAG-style retrieval before generation by retrieving relevant information from data sources and using it to improve the accuracy and relevance of generated responses [Chunk 1][Chunk 4].

**Average Score:** 0.6328

**Analysis:**

- Low context recall — the retrieval missed key chunks needed to answer.

### Failure Case 3

**Question:** In Amazon Bedrock, which feature searches your data to answer a query, and which feature evaluates both user inputs and model responses?

**Category:** multi_hop

**Ground Truth:** When a query is made, a knowledge base searches your data to find relevant information to answer the query. Amazon Bedrock Guardrails evaluates both user inputs and model responses.

**Predicted:** The feature that searches your data to answer a query is **Amazon Bedrock Knowledge Bases** [Chunk 1]. The feature that evaluates both retrieval effectiveness from data sources and the quality of generated responses is **Amazon Bedrock RAG evaluations** [Chunk 4].

**Average Score:** 0.7258

**Analysis:**

- Low answer correctness — the predicted answer diverges significantly from ground truth.

### No-Answer Behavior Summary

- True negatives (correct null): 4/4
- False positives (hallucinated answer): 0/4

## Correctness Score Distribution

- Distinct answer-correctness values (answerable rows): 0.30, 0.35, 0.52, 0.60, 0.61, 0.63, 0.64, 0.65, 0.67, 0.69, 0.70, 0.71, 0.74, 0.77, 0.84
- Min/Median/Max: 0.3000 / 0.6532 / 0.8417

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
