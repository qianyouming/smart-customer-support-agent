# Smart Customer Support Agent

A lightweight `FastAPI + RAG + SQLite` demo for customer-support Agent workflows.

This project is built as a learning and portfolio-ready MVP. It demonstrates how to combine session management, document ingestion, retrieval, citations, and persistence into a complete Agent-style application.

## Highlights

- Multi-turn chat with persistent session history
- Session create / rename / delete
- Document upload and parsing for `.txt`, `.md`, `.csv`, `.json`, and `.pdf`
- Simple RAG workflow with chunking and retrieval
- Citation display for retrieved knowledge
- Tool routing for calculator, mock support search, and retrieval
- Human handoff suggestion for unanswered or low-confidence cases
- Document detail page for viewing parsed chunks
- Automated tests and eval runner

## Screenshots

### Main Console

![Main UI](docs/screenshots/main-ui.png)

### RAG Answer With Citations

![RAG Answer](docs/screenshots/rag-answer.png)

### Session Management

![Session Management](docs/screenshots/session-management.png)

### Document Detail

![Document Detail](docs/screenshots/document-detail.png)

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

The project runs in mock mode by default. If you want to connect a real model, create a local `.env` file from `.env.example`.

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

## Run

```powershell
uvicorn app.main:app --reload
```

Open:

- Web UI: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Demo Flow

1. Open the web UI.
2. Create or select a session.
3. Ask a normal support question such as `How long does a refund take?`
4. Upload [sample_docs/agent_intro.txt](D:/knowledge-agent/sample_docs/agent_intro.txt)
5. Ask `What is RAG based on the uploaded document?`
6. Inspect citations and tool usage.
7. Open a document from the knowledge-base panel to inspect chunk content.

## Test

```powershell
python -m pytest
```

## Eval

```powershell
python -m evals.run_eval
```

Eval output:

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

This project is intentionally kept as a small Agent MVP instead of a heavy framework demo. It is meant to show:

- how session state is stored and managed
- how uploaded documents are parsed and chunked
- how retrieval is connected to answering
- how backend persistence supports product behavior
- how to verify an Agent workflow with tests and evals

## Future Improvements

- Replace keyword retrieval with embedding-based retrieval
- Upgrade SQLite to PostgreSQL + pgvector
- Add admin visibility for sessions and database inspection
- Improve document preview and retrieval quality
- Add real UI screenshots to this README
