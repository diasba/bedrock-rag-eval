# RAG

Containerized local RAG service with ingestion, hybrid retrieval, citations, evaluation tooling, and an agentic research endpoint.

## Overview
Build a local RAG (Retrieval-Augmented Generation) service that answers questions about a provided document corpus, then rigorously evaluate its quality using established benchmarks.  Your AI-assisted development process is encouraged.

---

## Part 1: Build a RAG Service
Build a containerized RAG pipeline that:

1. **Ingests documents**  
   - Accepts a folder of **Markdown / PDF / TXT** files as a knowledge base.  
   - For the evaluation corpus, use **AWS Bedrock documentation** — download a reasonable subset (**30–50 pages**).

2. **Chunks and embeds**  
   - Implement a chunking strategy (my choice: fixed-size).  
   - Store embeddings in a local vector database (chroma).

3. **Serves a REST API** with at minimum:
   - `POST /ingest` — triggers ingestion of a document folder
   - `POST /query` — accepts a natural language question, returns an answer with source citations
   - `GET /health` — returns service status

4. **Retrieves and generates**  
   - On query, retrieve top-k relevant chunks, pass them as context to an LLM, and return a grounded answer with references to source documents and **chunk IDs**.

---

## Technical Requirements

| Requirement | Constraint |
|---|---|
| **LLM** | Use an API with a free tier (Groq). API-Key will pe provided by me and must be stored according to the best practices of Software Engineering. |
| **Embeddings** | Local embeddings model (sentence-transformers/all-MiniLM-L6-v2). |
| **Vector Store** | **ChromaDB**. |
| **Containerization** | Must have a `docker-compose.yml` that brings up the full stack (app + vector DB). I will provide use a sample Dockerfile. |
| **Language** | **Python** (preferred) or **TypeScript**. |

---

## Part 2: Evaluate Your RAG Pipeline
This is equally important as building the service. You should demonstrate you understand how to measure RAG quality, not just build it.

### 2a. Create an Evaluation Dataset
Create a minimum of **20 question–answer–context triplets** based on your ingested corpus.

The dataset should include a mix of:
- Factual questions with clear, unambiguous answers
- Multi-hop questions that require synthesizing info from multiple chunks
- Questions with **no answer** in the corpus (to test hallucination resistance)
- Paraphrased questions (same question asked in a different way than the source text)

Example format:
```json
{
  "question": "What is the maximum number of tools you can pass in a single API request to Claude?",
  "ground_truth_answer": "You can pass up to 128 tools in a single API request.",
  "ground_truth_context": "The maximum number of tools that can be defined in a single API request is 128."
}
```

### 2b. Run Evaluation Metrics
Evaluate your pipeline using the following metrics (use **RAGAS** and **DeepEval**):

| Metric | What It Measures |
|---|---|
| **Context Precision** | Are the retrieved chunks actually relevant to the question? |
| **Context Recall** | Does retrieval find all the chunks needed to answer? |
| **Faithfulness** | Is the generated answer grounded in the retrieved context (no hallucination)? |
| **Answer Relevancy** | Does the generated answer actually address the question? |
| **Answer Correctness** | Does the generated answer match the ground truth? |

### 2c. Produce an Evaluation Report (can be done at later development stage)
Generate a structured report (**Markdown or HTML**) that includes:
- Aggregate scores per metric
- Per-question breakdown showing where the pipeline fails
- At least **3** specific failure cases with analysis of why they failed
- At least **2** concrete suggestions for improvements you would make if given more time

---

## Part 3: Documentation (can be done at later development stage)
Create a `README.md` that includes:
- Architecture diagram (ASCII, Mermaid, or image)
- Setup and run instructions (must work on a fresh machine with Docker)
- Design decisions and tradeoffs (chunking strategy, model choices, etc.)
- Known limitations
- What you would improve with more time


## Evaluation Criteria

| Criteria | Weight | What They're Looking For |
|---|---:|---|
| **Working System** | 25% | `docker-compose up` works, API responds correctly, answers are grounded |
| **RAG Quality & Evaluation** | 25% | Thoughtful eval dataset, correct use of metrics, insightful failure analysis |
| **Code Quality** | 15% | Clean structure, error handling, configuration management, type hints |
| **AI-Assisted Workflow** | 20% | Effective use of AI tools — problem decomposition, iterative refinement, not blind copy-paste |
| **Documentation & Design Decisions** | 15% | Clear README, justified tradeoffs, honest limitations |

---

## What They're NOT Looking For
- Over-engineering — don’t build a production system with auth, rate limiting, monitoring. Focus on the RAG pipeline and evaluation.
- Fine-tuned models — use off-the-shelf models; integration and evaluation matter, not model training.
- Spending money — everything should run on a laptop with 16 GB RAM and no paid API keys. If using an API, stick to free tiers.

---

## Hardware Expectations
The solution should run comfortably on:
- 16 GB RAM
- 4+ CPU cores
- ~20 GB free disk space (for Ollama models + vector DB)
- No GPU required (CPU inference is acceptable; it can be slow — that's fine)

---

## Tips
- Start with the simplest possible working pipeline, then iterate. A working basic system beats an ambitious broken one.
- Your AI coding session is a feature, not a secret. Show how you leverage these tools.
- The evaluation section is where strong candidates differentiate themselves. Don’t rush it.
- If you hit a wall, document it. Showing how you debug and work through problems (with or without AI) is valuable.

---


## Extra Credit: Add an Agentic Feature (can be done after MVP is implemented)
If you finish the core task and want to stand out, extend your RAG service with a creative agentic capability — something beyond simple question-answering by having the system take actions, make decisions, or chain multiple steps autonomously.

Examples:
- **Auto-research agent** — Generates sub-questions, queries the RAG pipeline for each, synthesizes a structured mini-report, identifies gaps.
- **Knowledge base curator** — Detects contradictions/outdated info across documents and suggests updates.
- **Comparative analyst** — Retrieves info about two topics, builds a structured comparison, highlights differences/similarities.
- **Query routing agent** — Classifies incoming questions, decides whether answerable from corpus or needs clarification; asks follow-ups if vague.

The implementation doesn’t need to be production-grade — they want creative thinking, a working proof of concept, and reasoning about usefulness in real deployments.

## Other Notes

No-answer questions must return answer=null and empty citations
Use .env locally, do not commit secrets, read via env vars, provide .env.example
Work MVP first, futher tasks will be provided later 