# Ask My Courses

A retrieval augmented generation (RAG) system that answers questions from course materials (syllabi, lecture slides, assignment sheets) and shows exactly which document, page and quote each answer came from. When the documents do not contain the answer, it says "I don't know" instead of guessing.

**Status:** in progress (see the [roadmap](docs/roadmap.md)). Live demo: _link added in Week 11_. Demo video: _added in Week 13_.

## Problem statement

University students juggle scattered course materials across dozens of PDFs and slide decks, and finding a specific policy, deadline, or topic often means digging through files instead of getting a direct answer. This bot answers questions from students in a specific course, such as when a topic is covered, what a policy states, or when an assignment is due, by retrieving the answer directly from the actual syllabus, slides, and assignment sheets rather than making them search through documents manually. It refuses to answer when the evidence is not in the documents.

## Why this project exists

Most RAG demos stop at "it retrieves something and answers." This project treats retrieval quality as something to measure and improve, not assume. Every major design choice (chunking, embedding model, search strategy, reranking, refusal threshold) is tested against a hand-labeled evaluation set with a held-out test split, and every result is reported with a confidence interval, latency and cost. Changes that did not help are documented too (see [Negative results](#negative-results)).

## What it does

A student can ask a question like "what is the late submission policy for CENG301" or "when do we cover dynamic programming" and get an answer grounded in the course documents, with citations to the source file, page and quote. Each citation is verified: the quoted span must actually appear in a retrieved chunk, otherwise it is dropped.

When a question needs structured or time-based information, such as an exam date or an assignment deadline, the model can call one of two read-only tools (a calendar tool reading an `.ics` schedule and a structured-data lookup) instead of relying only on retrieved text. The model decides whether to retrieve, call a tool, do both, or answer directly, and that decision is itself evaluated.

## Data

The public demo runs on **100+ publicly licensed documents** from one domain (sources and licenses are listed in [`data/README.md`](data/README.md)), because private course slides cannot be redistributed and a small corpus makes every improvement look like noise. My own course documents are kept private (`data/private/`, git-ignored) and used only as a generalization test.

## Evaluation

### Method

- **Golden set:** 80-120 questions (simple lookups, multi-part questions, paraphrased questions, and about 15% unanswerable ones), split into a **dev** set for tuning and a frozen **test** set for reporting. Real user failures are collected in a separate `prod_failures` set so the test set is never contaminated.
- **Labels:** evidence is labeled by document, page and quote span, not by chunk ID, so labels survive re-chunking.
- **Retrieval metrics:** Recall@k, MRR and nDCG@10, computed deterministically from the labels.
- **Answer metrics:** faithfulness and answer correctness via RAGAS with a pinned judge (fixed model, temperature 0, different from the generator), run 3 times to report variance.
- **Refusal:** refusal accuracy on unanswerable questions and false-refusal rate on answerable ones, reported separately.
- **Statistics:** 95% bootstrap confidence intervals everywhere; differences between pipelines use a paired bootstrap.
- **Baselines:** a closed-book LLM (no retrieval) and the naive pipeline, so gains from retrieval are real and not just model knowledge.

### Results (test set)

All numbers are TBD until the evaluation harness (Week 2) and the later pipeline stages are built. Latency is p50/p95 in milliseconds on the stated hardware; cost is USD per 1,000 queries.

| Pipeline | Recall@5 (95% CI) | MRR | nDCG@10 | Faithfulness | p50 / p95 latency | Cost / 1k queries |
|---|---|---|---|---|---|---|
| Closed-book (no retrieval) | n/a | n/a | n/a | TBD | TBD | TBD |
| Naive retrieval | TBD | TBD | TBD | TBD | TBD | TBD |
| + Better parsing and chunking | TBD | TBD | TBD | TBD | TBD | TBD |
| + Hybrid search (Postgres full-text + vectors, RRF) | TBD | TBD | TBD | TBD | TBD | TBD |
| + Cross-encoder reranking | TBD | TBD | TBD | TBD | TBD | TBD |
| + Grounding, refusal threshold, verified citations | TBD | TBD | TBD | TBD | TBD | TBD |

| Behavior | Result |
|---|---|
| Refusal accuracy (unanswerable questions) | TBD |
| False-refusal rate (answerable questions) | TBD |
| Citation accuracy (cited span supports the claim) | TBD |
| Tool-selection accuracy (correct tool, correct arguments) | TBD |
| Prompt-injection test cases passed | TBD / 10 |

### Failure analysis

Failures from the test set and from real users are classified into: parsing, chunking, retrieval miss, ranking miss, generation error, bad refusal. Counts and the one failure I investigated in depth are written up in [`docs/failure_story.md`](docs/failure_story.md). _Added in Week 12._

### Negative results

Things I tried that did not help, with numbers, are listed in [`docs/decision_log.md`](docs/decision_log.md). _Filled in as the project progresses._

## Architecture

```
documents -> parse -> chunk (+ metadata) -> embed -> Postgres (pgvector + full-text index)

question -> keyword search + vector search -> RRF fusion -> cross-encoder rerank
         -> refusal check -> LLM (grounded, structured output) -> citation verification
         -> answer + verified citations
                |
                +-- may call tools: calendar (.ics), structured data lookup (read-only)
```

Documents are parsed and split into chunks with source metadata (file, page, section). Each chunk is embedded and stored in **Postgres with pgvector**, alongside a full-text index. At query time, keyword and vector results are fused with reciprocal rank fusion, then reranked with a cross-encoder. If the top reranker score is below a tuned threshold, the system refuses. Otherwise the language model answers in a structured format with citations, and every citation is verified against the retrieved text. The pipeline is a standalone Python package served by a **FastAPI** backend (with streaming responses) and a thin **Streamlit** client. Every request writes one JSON line to a log: query, retrieved chunk IDs and scores, per-stage latency, tokens, cost and refusal flag.

## Tech stack

Python, FastAPI, Streamlit, Postgres + pgvector (Chroma only in the first prototype), sentence-transformers for embeddings and reranking, Postgres full-text search for keyword retrieval (`rank_bm25` kept as an offline reference), RAGAS for answer-level evaluation, pytest and ruff, Docker, GitHub Actions, and an LLM provider for generation. The retrieval, fusion and reranking logic is written from scratch rather than hidden behind a framework.

## Project structure

```
ask-my-courses/
  data/
    raw/                public documents (see data/README.md for sources and licenses)
    private/            my own course files, git-ignored
  eval/
    golden_set.json     labeled questions with dev/test split
    runs/               one JSON file per evaluation run (config, commit, metrics)
    run_eval.py         runs the pipeline over the golden set and prints the tables
    known_issues.md
  docs/
    decision_log.md     every decision, its evidence, and the alternative rejected
    error_taxonomy.md
    parsing_notes.md
    security.md
    failure_story.md
  src/
    pipeline/
      ingest.py         parsing, chunking, metadata
      embedding.py      embedding models
      retriever.py      Retriever interface, pgvector, full-text, RRF
      rerank.py         cross-encoder reranking
      generator.py      grounded generation, refusal, citation verification
      tools.py          calendar and structured-data tools, agent loop
    api.py              FastAPI app (/ask, /ask/stream, /feedback, /health)
  tests/                pytest tests (chunking, metrics, fusion, citations, API)
  app.py                Streamlit client
  docker-compose.yml    api + postgres + ui
  Dockerfile
  Makefile              make eval, make test, make lint
  README.md
  requirements.txt
  .env.example
  .gitignore
```

Some of these files do not exist yet; the project is built week by week.

## Setup

Clone the repository and create a virtual environment.

```
git clone https://github.com/UmutAA/ask-my-courses.git
cd ask-my-courses
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your API keys.

```
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/askmycourses
```

Start Postgres with pgvector, place documents in `data/raw`, then build the index.

```
docker compose up -d postgres
python src/pipeline/ingest.py
```

Or start everything with one command:

```
docker compose up
```

## Running the app

Start the backend.

```
uvicorn src.api:app --reload
```

Start the frontend in a separate terminal.

```
streamlit run app.py
```

The API documentation is available at `http://localhost:8000/docs`.

## Running the evaluation

```
make eval
```

This runs every question in the golden set through the pipeline and regenerates the tables in this README: Recall@k, MRR, nDCG, faithfulness, refusal accuracy, citation accuracy, latency and cost, each with 95% confidence intervals. Each run is saved to `eval/runs/` with its configuration and git commit so any number can be reproduced. A small smoke version of the evaluation (retrieval only, no paid LLM calls) runs in CI and fails if Recall@5 drops below the stored baseline.

## Security and cost protection

The public demo runs in capped mode: per-IP rate limiting, a daily question limit, a global daily budget with an environment-variable kill switch, capped question length and output tokens, API-key protection on admin routes, and a locked-down CORS origin. Retrieved text and tool output are treated as untrusted input, tools are read-only, and the agent loop is capped at 4 steps. I tested 8-10 prompt-injection cases; the results and the remaining open risks are in [`docs/security.md`](docs/security.md). Queries are logged and users are told so in the UI.

## Current limitations

Retrieval quality depends heavily on document formatting, and scanned or image-heavy slides rely on OCR that is only partially reliable. Prompt injection is mitigated, not solved. The tool layer supports a small fixed set of read-only tools rather than general tool discovery. Exact vector search is used because the corpus is small; behavior at millions of documents has not been tested, and I make no claims about it. The evaluation set is small enough that small differences between pipelines may not be statistically significant, which is why confidence intervals are reported.

## Planned improvements

Query rewriting and decomposition for multi-part questions, an agentic layer that can ask a clarifying question, a second structured data source such as a course schedule database, fine-tuning a small embedding model or reranker on synthetic query-passage pairs, and a larger-scale index test comparing HNSW with exact search.

## License

MIT