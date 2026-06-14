# Smart Customer Support Agent

A lightweight Agent + RAG demo built with `FastAPI`, `SQLite`, and a simple web UI.

This project is designed for learning, demos, and internship portfolios. It focuses on a complete but approachable workflow:

`user question -> tool routing -> retrieval/search -> structured answer -> citations -> session persistence`

## Features

- Multi-turn chat with persistent sessions
- Session create / rename / delete
- Document upload with `.txt`, `.md`, `.csv`, `.json`, and `.pdf` support
- Simple RAG pipeline with chunking and keyword-based retrieval
- Citation display for retrieved content
- Tool routing for calculator, mock support search, and retrieval
- Human handoff suggestion for low-confidence or missing knowledge cases
- Document detail page for inspecting parsed chunks
- SQLite persistence for sessions, messages, documents, chunks, and eval results
- Automated tests and a small eval runner

## Tech Stack

- Backend: `FastAPI`, `SQLAlchemy`, `Pydantic`
- Frontend: `HTML`, `CSS`, `Vanilla JavaScript`
- Database: `SQLite`
- File parsing: `pypdf`
- Testing: `pytest`

## Project Structure

```text
app/
  api/          HTTP routes
  core/         configuration
  db/           models, session, CRUD
  llm/          model client
  rag/          extract, chunk, ingest, retrieve
  schemas/      request / response models
  services/     application services
  static/       web UI
  tools/        calculator, search, retrieval
evals/          eval runner and report
sample_docs/    demo documents
tests/          automated tests
```

## Quick Start

```powershell
cd D:\knowledge-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Environment

This project runs in mock mode by default. If you want to connect a real model, create a local `.env` file based on `.env.example`.

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=
USE_REAL_LLM=false
MODEL=gpt-4.1-mini
DEBUG=true
DATA_DIR=data
DATABASE_URL=sqlite:///data/knowledge_agent.db
```

To use a real model:

```env
USE_REAL_LLM=true
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
```

## Run the App

```powershell
uvicorn app.main:app --reload
```

Open:

- Web UI: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Demo Flow

1. Open the web UI.
2. Create or select a session.
3. Ask a normal question such as `退款周期是多久？`
4. Upload [sample_docs/agent_intro.txt](D:/knowledge-agent/sample_docs/agent_intro.txt)
5. Ask `根据上传文档回答：RAG 是什么？`
6. Inspect citations and tool usage.
7. Open a document from the knowledge-base panel to view chunk details.

## Testing

```powershell
python -m pytest
```

## Eval

```powershell
python -m evals.run_eval
```

The eval report is written to:

```text
evals/eval_report.json
```

## Database

Default database file:

```text
data/knowledge_agent.db
```

Main tables:

- `sessions`
- `messages`
- `documents`
- `document_chunks`
- `tool_calls`
- `eval_runs`
- `eval_results`

## Why This Project

This project is intentionally built as a small Agent MVP instead of a large framework-heavy system. The goal is to understand and demonstrate:

- how session state is managed
- how documents are parsed and chunked
- how retrieval is wired into answering
- how backend persistence supports the product experience
- how to test a full Agent-style workflow

## Next Improvements

- Replace keyword retrieval with embedding-based retrieval
- Upgrade SQLite to PostgreSQL + pgvector
- Improve document preview and admin visibility
- Add better session search and filters
- Add screenshot assets for the GitHub page
