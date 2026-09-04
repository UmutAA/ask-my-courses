# Ask My Courses

A retrieval augmented generation system built over university course materials. It answers questions using syllabi, lecture slides, and assignment documents, and shows exactly which source each answer came from.

## Problem statement
 
University students juggle scattered course materials across dozens of PDFs and slide decks, and finding a specific policy, deadline, or topic often means digging through files instead of getting a direct answer. This bot answers questions from students in a specific course, such as when a topic is covered, what a policy states, or when an assignment is due, by retrieving the answer directly from the actual syllabus, slides, and assignment sheets for that course rather than requiring them to search through documents manually.

## Why this project exists

Most RAG demos stop at "it retrieves something and answers." This project treats retrieval quality as something to measure and improve, not assume. Every major design choice in this repo, including chunk size, search strategy, and reranking, was tested against a hand built evaluation set rather than picked by guesswork.

## What it does

A student can ask a question like "what is the late submission policy for CENG301" or "when do we cover dynamic programming" and get an answer grounded in the actual course documents, with citations to the source file and page. When a question needs live information, such as an upcoming deadline or the weather on exam day, the system can also call external APIs instead of relying only on retrieved documents.

## Evaluation results

Retrieval and answer quality were measured using RAGAS across three stages of the pipeline. Numbers below are averaged across a 40 question golden evaluation set.

| Stage | Context precision | Context recall | Faithfulness |
|---|---|---|---|
| Naive retrieval | TBD | TBD | TBD |
| Hybrid search (BM25 + vectors) | TBD | TBD | TBD |
| Hybrid search with reranking | TBD | TBD | TBD |


## Architecture

Documents are parsed and split into chunks with attached source metadata. Each chunk is embedded and stored in a vector database. At query time, results from keyword search and vector search are combined, then reranked with a cross encoder before being passed to the language model. The model can also call external tools, such as a calendar or weather API, when a question requires information outside the document set. The pipeline is served through a FastAPI backend with a Streamlit frontend.

## Tech stack

Python, FastAPI, Streamlit, Chroma for vector storage, sentence transformers for embeddings and reranking, rank_bm25 for keyword search, RAGAS for evaluation, and an LLM provider for generation.

## Project structure

```
ask-my-courses/
  data/
    raw/              original course documents
  eval/
    golden_set.json   hand written question and answer pairs used for evaluation
    results/          saved evaluation runs for each pipeline stage
  src/
    ingest.py         parsing and chunking
    embed.py          embedding and vector store setup
    retrieve.py        hybrid search and reranking
    tools.py           external API integrations
    api.py             FastAPI backend
  app.py                Streamlit frontend
  README.md
```

## Setup

Clone the repository and create a virtual environment.

```
git clone https://github.com/UmutAA/ask-my-courses.git
cd ask-my-courses
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add your API keys to a .env file.

```
OPENAI_API_KEY=your_key_here
```

Place course documents in data/raw, then run the ingestion script to build the vector store.

```
python src/ingest.py
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

## Running the evaluation

```
python eval/run_eval.py
```

This runs every question in the golden set through the pipeline and prints context precision, context recall, and faithfulness scores.

## Current limitations

Retrieval quality depends heavily on document formatting, and scanned or image heavy slides are not yet handled well. The tool calling layer currently supports a small fixed set of external APIs rather than general purpose tool discovery. There is no authentication on the API yet, so it should not be exposed publicly without adding one.

## Planned improvements

Query decomposition for multi part questions, support for a second structured data source such as a course schedule database, and basic user authentication before any public deployment.

## License

MIT