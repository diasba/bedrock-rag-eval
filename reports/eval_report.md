# RAG Evaluation Report

Generated: 2026-02-16 15:44:26

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
| Context Precision | 0.6208 |
| Context Recall | 0.6417 |
| Faithfulness | 0.8275 |
| Answer Relevancy | 0.5699 |
| Answer Correctness | 0.6831 |

## Answerable-Only Scores

| Metric | Score |
|---|---|
| Context Precision | 0.7760 |
| Context Recall | 0.8021 |
| Faithfulness | 0.9719 |
| Answer Relevancy | 0.7124 |
| Answer Correctness | 0.6038 |

## No-Answer Contract

- No-answer questions: 4
- Correct null responses (answer=null): 4
- Hallucinated answers on no-answer rows: 0

## Scores by Category

### factual (7 questions)

- Context Precision: 0.9167
- Context Recall: 0.8571
- Faithfulness: 0.9357
- Answer Relevancy: 0.7908
- Answer Correctness: 0.5972

### multi_hop (4 questions)

- Context Precision: 0.6250
- Context Recall: 0.6250
- Faithfulness: 1.0000
- Answer Relevancy: 0.7472
- Answer Correctness: 0.6417

### no_answer (4 questions) (Correct, because answer is not being expected)

- Context Precision: 0.0000
- Context Recall: 0.0000
- Faithfulness: 0.2500
- Answer Relevancy: 0.0000
- Answer Correctness: 1.0000

### paraphrase (5 questions)

- Context Precision: 0.7000
- Context Recall: 0.8667
- Faithfulness: 1.0000
- Answer Relevancy: 0.5749
- Answer Correctness: 0.5828

## Per-Question Breakdown

| # | Question | Category | Ctx Prec | Ctx Rec | Faith | Ans Rel | Ans Corr |
|---|---|---|---|---|---|---|---|
| 1 | What is Amazon Bedrock? | factual | 1.00 | 1.00 | 1.00 | 0.93 | 0.62 |
| 2 | Do you need model access permissions before using … | factual | 0.58 | 1.00 | 1.00 | 0.78 | 0.61 |
| 3 | Where can you find supported models for Bedrock? | factual | 1.00 | 1.00 | 1.00 | 0.82 | 0.47 |
| 4 | What is a Bedrock Knowledge Base used for? | factual | 1.00 | 1.00 | 0.80 | 0.79 | 0.68 |
| 5 | What does chunking do in a knowledge base pipeline… | factual | 0.83 | 0.00 | 0.75 | 0.84 | 0.49 |
| 6 | What is the purpose of RetrieveAndGenerate? | factual | 1.00 | 1.00 | 1.00 | 0.60 | 0.59 |
| 7 | What is enabled by default with the correct AWS Ma… | multi_hop | 0.00 | 0.50 | 1.00 | 0.47 | 0.77 |
| 8 | In fixed-size chunking, what two settings define c… | multi_hop | 0.50 | 1.00 | 1.00 | 0.90 | 0.84 |
| 9 | In Amazon Bedrock, which feature searches your dat… | multi_hop | 1.00 | 0.50 | 1.00 | 0.78 | 0.35 |
| 10 | For Amazon Bedrock inference, which endpoint is us… | multi_hop | 1.00 | 0.50 | 1.00 | 0.83 | 0.61 |
| 11 | Can Bedrock KB do RAG-style retrieval before gener… | paraphrase | 0.75 | 1.00 | 1.00 | 0.73 | 0.70 |
| 12 | How do I check token count before sending a prompt… | paraphrase | 1.00 | 1.00 | 1.00 | 0.65 | 0.67 |
| 13 | Is there an API for streaming model responses? | paraphrase | 0.75 | 1.00 | 1.00 | 0.79 | 0.66 |
| 14 | Can I directly apply a guardrail through an API ca… | paraphrase | 1.00 | 1.00 | 1.00 | 0.66 | 0.72 |
| 15 | Name at least 5 runtime invocation metrics Bedrock… | paraphrase | 0.00 | 0.33 | 1.00 | 0.04 | 0.17 |
| 16 | In Amazon Bedrock inference, which service tier is… | factual | 1.00 | 1.00 | 1.00 | 0.78 | 0.72 |
| 17 | What is the default PostgreSQL version used intern… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| 18 | Which color theme does the AWS Bedrock console use… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| 19 | What salary does an AWS Bedrock product manager ea… | no_answer | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 |
| 20 | What was the weather in Seattle when Bedrock launc… | no_answer | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |

## Failure Analysis

### Failure Case 1

**Question:** Name at least 5 runtime invocation metrics Bedrock publishes (CloudWatch)

**Category:** paraphrase

**Ground Truth:** Amazon Bedrock tracks Invocations, InvocationLatency, InvocationClientErrors, InvocationServerErrors, InvocationThrottles, InputTokenCount, OutputTokenCount, LegacyModelInvocations, and OutputImageCount.

**Predicted:** The following table describes runtime invocation metrics provided by Amazon Bedrock.

**Average Score:** 0.3087

**Analysis:**

- Low context precision — retrieved chunks were not relevant to this question.
- Low context recall — the retrieval missed key chunks needed to answer.
- Low answer relevancy — the generated answer does not address the question directly.
- Low answer correctness — the predicted answer diverges significantly from ground truth.

### Failure Case 2

**Question:** What is enabled by default with the correct AWS Marketplace permissions, and which table shows model support by AWS Region?

**Category:** multi_hop

**Ground Truth:** Access to all Amazon Bedrock foundation models is enabled by default with the correct AWS Marketplace permissions. Model support by AWS Region is shown in the model support by AWS Region table.

**Predicted:** Access to all Amazon Bedrock foundation models is enabled by default with the correct AWS Marketplace permissions [Chunk 1]. The table showing inference profile support by AWS Region is found in the "Supported Regions and models for inference profiles" section [Chunk 2].

**Average Score:** 0.5475

**Analysis:**

- Low context precision — retrieved chunks were not relevant to this question.
- Low answer relevancy — the generated answer does not address the question directly.

### Failure Case 3

**Question:** What does chunking do in a knowledge base pipeline?

**Category:** factual

**Ground Truth:** Chunking splits documents into smaller segments so they can be efficiently embedded and retrieved during a query.

**Predicted:** Chunking splits each document in your data source into smaller subdivisions (chunks) based on token count and other parameters, which are then used to populate the `$search_results$` placeholder in the knowledge base prompt templates [Chunk 3]. This process helps shorten the content filled in the prompt templates, improving retrieval and generation efficiency [Chunk 1][Chunk 2].

**Average Score:** 0.5815

**Analysis:**

- Low context recall — the retrieval missed key chunks needed to answer.
- Low answer correctness — the predicted answer diverges significantly from ground truth.

### No-Answer Behavior Summary

- True negatives (correct null): 4/4
- False positives (hallucinated answer): 0/4

## Correctness Score Distribution

- Distinct answer-correctness values (answerable rows): 0.17, 0.35, 0.47, 0.49, 0.59, 0.61, 0.62, 0.66, 0.67, 0.68, 0.70, 0.72, 0.77, 0.84
- Min/Median/Max: 0.1708 / 0.6565 / 0.8417

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
