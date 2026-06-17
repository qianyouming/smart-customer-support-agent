# Development Guide - Smart Customer Support Agent

**Architecture, Request Flow, and Deployment Notes**

这份文档面向开发者，重点解释这个项目是怎么组织的、核心链路怎么跑、以及后续该怎么维护和扩展。

**快速导航**

- [项目目标](#goal)
- [系统架构](#architecture)
- [核心链路](#flows)
- [目录职责](#structure)
- [主要接口](#api)
- [数据存储](#data)
- [本地开发](#local-dev)
- [测试与评测](#test-eval)
- [Docker 与部署](#deploy)
- [常见问题](#faq)
- [建议学习顺序](#learn)

---

<a id="goal"></a>

## 项目目标

这个项目不是为了堆很多框架，而是为了做一个边界清晰、方便讲解、可以完整演示的 Agent MVP。

它重点展示四件事：

1. 一个 Agent 应用如何组织前后端
2. 一个 RAG 流程如何从上传文档走到生成回答
3. 一个会话系统如何和知识库、工具调用组合在一起
4. 一个项目如何从本地开发走到 Docker 和云服务器部署

---

<a id="architecture"></a>

## 系统架构

整体可以拆成 5 层：

### 1. Frontend

负责用户交互：

- 会话列表展示与切换
- 消息输入与回答渲染
- 文档上传
- 文档详情查看
- 引用与工具调用结果展示

### 2. API Layer

由 `FastAPI` 提供 HTTP 接口，负责：

- 接收前端请求
- 调用服务层
- 返回结构化 JSON

### 3. Service / Agent Layer

负责编排核心业务逻辑：

- 保存用户消息
- 触发工具路由
- 组装上下文
- 调用 mock 或真实模型
- 保存最终回答

### 4. RAG Layer

负责知识库能力：

- 文档解析
- chunk 切分
- 文档入库
- 相关内容检索
- 引用来源组织

### 5. Persistence Layer

使用 `SQLite + SQLAlchemy` 保存：

- 会话
- 消息
- 文档
- 文档切片
- 工具调用
- 评测结果

整体链路如下：

```text
Frontend
   |
   v
FastAPI API
   |
   +--> Session / Message persistence
   +--> Document upload / parse / chunk / ingest
   +--> Tool routing
   +--> Retrieval
   +--> LLM or mock response
   |
   v
SQLite
```

---

<a id="flows"></a>

## 核心链路

### 1. 聊天请求链路

用户提问后，系统会执行：

```text
Create / select session
-> save user message
-> decide tool route
-> optionally retrieve context
-> generate answer
-> save assistant message
-> return answer to frontend
```

这个链路的核心是：会话状态、工具调用、回答生成都被纳入同一个请求闭环。

### 2. 文档上传链路

用户上传文档后，系统会执行：

```text
Upload file
-> parse file content
-> chunk text
-> store document metadata
-> store document chunks
-> expose document list to frontend
```

当前支持：

- `.txt`
- `.md`
- `.csv`
- `.json`
- `.pdf`

### 3. RAG 问答链路

当用户问“根据上传文档回答”这类问题时，系统会执行：

```text
User question
-> retrieve related chunks
-> pack context
-> call mock or real LLM
-> answer with citations
```

当前项目使用轻量关键词检索，适合 MVP 和教学理解。

### 4. 工具调用链路

当前内置工具：

- `calculator`
- `search`
- `retrieval`

工具路由采用轻量规则方式，重点是让你看清楚：

- Agent 为什么会调这个工具
- 工具结果怎么回流到回答里
- 工具调用如何被记录

---

<a id="structure"></a>

## 目录职责

```text
app/
  agent/      Agent 状态与执行流
  api/        HTTP 接口层
  core/       配置、日志
  db/         数据模型、数据库连接、CRUD
  llm/        模型客户端、提示词、输出解析
  rag/        文档解析、切块、入库、检索
  schemas/    请求响应模型
  services/   业务编排层
  static/     前端页面与脚本
  tools/      工具注册与实现
docs/         开发文档与截图
evals/        评测脚本
sample_docs/  演示文档
tests/        自动化测试
```

理解顺序建议是：

- 先看 `app/api`
- 再看 `app/services`
- 再看 `app/rag`
- 再看 `app/db`
- 最后看 `app/llm` 和 `app/tools`

---

<a id="api"></a>

## 主要接口

项目启动后可以在 `/docs` 查看完整 Swagger 文档。

常见接口如下：

- `GET /health`
  健康检查。
- `GET /api/sessions`
  获取会话列表。
- `POST /api/sessions`
  创建会话。
- `PATCH /api/sessions/{session_id}`
  重命名会话。
- `DELETE /api/sessions/{session_id}`
  删除会话。
- `POST /api/chat`
  发送消息并获取回答。
- `POST /api/files/upload`
  上传文档。
- `GET /api/files`
  获取文档列表。

---

<a id="data"></a>

## 数据存储

默认数据库文件：

```text
data/knowledge_agent.db
```

主要数据表：

- `sessions`
- `messages`
- `documents`
- `document_chunks`
- `tool_calls`
- `eval_runs`
- `eval_results`

这些表一起支撑了：

- 会话历史追踪
- 知识库管理
- 工具调用记录
- 自动化评测记录

---

<a id="local-dev"></a>

## 本地开发

### 方式 A：Python 本地运行

```powershell
cd D:\knowledge-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

访问入口：

- Web UI: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`

### 方式 B：Docker 运行

```powershell
docker compose up --build
```

---

<a id="test-eval"></a>

## 测试与评测

### 单元测试

```powershell
python -m pytest
```

### 评测脚本

```powershell
python -m evals.run_eval
```

评测输出位置：

```text
evals/eval_report.json
```

测试主要覆盖：

- 聊天接口
- 文档解析
- 前端页面可用性
- 检索逻辑
- 工具调用

---

<a id="deploy"></a>

## Docker 与部署

### 本地容器运行

```powershell
docker compose up --build
```

### 云服务器部署思路

推荐链路：

```text
GitHub -> 云服务器 -> Docker Compose -> Nginx -> 公网访问
```

基本步骤：

1. 安装 Docker 和 docker-compose
2. 拉取项目代码
3. 配置 `.env`
4. 运行 `docker-compose up -d --build`
5. 使用 Nginx 反向代理到 `8000`
6. 放行服务器防火墙端口

---

<a id="faq"></a>

## 常见问题

### 为什么默认不是调用真实模型

因为 `mock` 模式更适合：

- 零成本演示
- 本地开发
- 自动化测试
- 避免 API key 泄露

### 为什么不用向量数据库

因为这个项目定位是 MVP。先把上传、切块、检索、回答、持久化主链路讲清楚，比一开始就上更重的基础设施更重要。

### 为什么有前端

前端不只是展示层，它承担：

- 提问入口
- 会话管理
- 文档上传
- 文档详情查看
- 回答与引用展示

没有前端时，这更像接口 demo；有前端后，它更像一个可以直接演示的产品。

### 真实模型接口在哪里打开

不在 GitHub 打开，而是在运行环境的 `.env` 里配置：

```env
USE_REAL_LLM=true
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
MODEL=your_model_name
```

---

<a id="learn"></a>

## 建议学习顺序

建议按这个顺序理解项目：

1. 先跑通项目，理解完整产品流程
2. 看 `app/api`，理解接口层
3. 看 `app/services`，理解业务编排
4. 看 `app/rag`，理解知识库链路
5. 看 `app/db`，理解数据如何落库
6. 看 `app/llm` 和 `app/tools`，理解模型与工具调用

如果你是为了面试，优先讲清楚这三条主线：

- 一次聊天请求怎么流转
- 一次文档上传怎么入库
- 一次 RAG 回答怎么生成
