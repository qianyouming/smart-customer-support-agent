# Smart Customer Support Agent | 智能客服知识库 Agent

一个基于 `FastAPI + RAG + SQLite` 的智能客服 Agent 示例项目，用于学习、演示和实习作品集展示。

A lightweight `FastAPI + RAG + SQLite` demo for customer-support Agent workflows, designed for learning, demos, and internship portfolios.

本项目展示了如何把多轮会话、文档上传、知识库检索、引用展示、工具调用和数据持久化串成一个完整的 Agent 应用闭环。

It demonstrates how to combine multi-turn sessions, document ingestion, retrieval, citations, tool routing, and persistence into a complete Agent-style application.

## 项目亮点 | Highlights

- 支持多轮客服会话，并将会话历史持久化保存
- 支持会话创建、重命名、删除和历史记录查看
- 支持 `.txt`、`.md`、`.csv`、`.json`、`.pdf` 文档上传与解析
- 实现简单 RAG 流程，包括文档切分、检索和引用展示
- 支持计算器、模拟客服搜索、知识库检索等工具调用
- 对无法回答或证据不足的问题给出人工转接建议
- 提供文档详情页，可查看上传文档被解析后的 chunks
- 使用 `pytest` 和 eval 脚本验证核心链路

English:

- Multi-turn chat with persistent session history
- Session create, rename, delete, and history lookup
- Document upload and parsing for `.txt`, `.md`, `.csv`, `.json`, and `.pdf`
- Simple RAG workflow with chunking, retrieval, and citations
- Tool routing for calculator, mock support search, and retrieval
- Human handoff suggestion for unanswered or low-confidence cases
- Document detail page for inspecting parsed chunks
- Automated tests and eval runner

## 项目截图 | Screenshots

### 主控制台 | Main Console

![Main UI](docs/screenshots/main-ui.png)

### RAG 问答与引用 | RAG Answer With Citations

![RAG Answer](docs/screenshots/rag-answer.png)

### 会话管理 | Session Management

![Session Management](docs/screenshots/session-management.png)

### 文档详情 | Document Detail

![Document Detail](docs/screenshots/document-detail.png)

## 技术栈 | Tech Stack

- 后端 Backend: `FastAPI`, `SQLAlchemy`, `Pydantic`
- 前端 Frontend: `HTML`, `CSS`, `Vanilla JavaScript`
- 数据库 Database: `SQLite`
- 文档解析 File parsing: `pypdf`
- 测试 Testing: `pytest`

## 项目结构 | Project Structure

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

## 快速开始 | Quick Start

```powershell
cd D:\knowledge-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 环境变量 | Environment

项目默认使用 mock 模式运行，不需要真实模型 API。若需要连接真实模型，可以基于 `.env.example` 创建本地 `.env` 文件。

The project runs in mock mode by default, so no real model API is required. To connect a real model, create a local `.env` file from `.env.example`.

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=
USE_REAL_LLM=false
MODEL=gpt-4.1-mini
DEBUG=true
DATA_DIR=data
DATABASE_URL=sqlite:///data/knowledge_agent.db
```

启用真实模型：

To use a real model:

```env
USE_REAL_LLM=true
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
```

## 启动项目 | Run

```powershell
uvicorn app.main:app --reload
```

打开页面：

Open:

- Web UI: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 演示流程 | Demo Flow

1. 打开 Web UI。
2. 新建或选择一个会话。
3. 提问普通客服问题，例如 `退款周期是多久？`
4. 上传 [sample_docs/agent_intro.txt](sample_docs/agent_intro.txt)
5. 提问 `根据上传文档回答：RAG 是什么？`
6. 查看回答、引用来源和工具调用过程。
7. 点击知识库中的文档，进入文档详情页查看 chunk 内容。

English:

1. Open the web UI.
2. Create or select a session.
3. Ask a normal support question such as `How long does a refund take?`
4. Upload [sample_docs/agent_intro.txt](sample_docs/agent_intro.txt)
5. Ask `What is RAG based on the uploaded document?`
6. Inspect the answer, citations, and tool trace.
7. Open a document from the knowledge-base panel to inspect chunk content.

## 测试 | Test

```powershell
python -m pytest
```

## 评测 | Eval

```powershell
python -m evals.run_eval
```

评测结果输出到：

Eval output:

```text
evals/eval_report.json
```

## 数据库 | Database

默认数据库文件：

Default database file:

```text
data/knowledge_agent.db
```

主要数据表：

Main tables:

- `sessions`
- `messages`
- `documents`
- `document_chunks`
- `tool_calls`
- `eval_runs`
- `eval_results`

## 项目价值 | Why This Project

这个项目刻意保持为一个轻量级 Agent MVP，而不是依赖大量框架封装。它更适合用来展示：

This project is intentionally kept as a small Agent MVP instead of a heavy framework demo. It is meant to show:

- 会话状态如何存储和管理
- 文档如何解析、切分并进入知识库
- 检索结果如何参与回答生成
- 后端持久化如何支撑产品体验
- 如何用测试和评测脚本验证 Agent 核心链路

English:

- how session state is stored and managed
- how uploaded documents are parsed and chunked
- how retrieval is connected to answering
- how backend persistence supports product behavior
- how to verify an Agent workflow with tests and evals

## 后续优化 | Future Improvements

- 将关键词检索升级为 embedding 检索
- 将 SQLite 升级为 PostgreSQL + pgvector
- 增加后台管理页，便于查看会话、消息和文档数据
- 优化文档预览和检索质量
- 引入更完整的 Agent 工作流编排

English:

- Replace keyword retrieval with embedding-based retrieval
- Upgrade SQLite to PostgreSQL + pgvector
- Add an admin page for sessions, messages, and documents
- Improve document preview and retrieval quality
- Add more complete Agent workflow orchestration
