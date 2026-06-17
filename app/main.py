"""FastAPI 应用入口模块。

本模块负责组装 API 路由、初始化数据库，并提供演示 UI 所需的静态页面服务。
整体架构：FastAPI + SQLite + RAG + 工具调用，构成一个轻量级智能客服 Agent。
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.files import router as files_router
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.db.session import init_db

# 项目根目录和静态资源目录
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期管理：在开始接受请求前完成数据库表创建和轻量级迁移。"""
    init_db()
    yield


app = FastAPI(
    title="Smart Customer Support Agent",
    description="A FastAPI customer-support agent with tools, retrieval, persistence, and evals.",
    version="0.2.0",
    lifespan=lifespan,
)

# 注册各功能模块的路由
app.include_router(health_router)       # 健康检查
app.include_router(chat_router)         # 聊天对话
app.include_router(files_router)        # 文件/知识库管理
app.include_router(sessions_router)     # 会话管理
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """返回主聊天控制台页面。"""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/documents/{document_id}", include_in_schema=False)
def document_detail_page(document_id: str) -> FileResponse:
    """返回文档详情页面，具体数据由页面脚本异步加载。"""
    return FileResponse(STATIC_DIR / "document.html")
