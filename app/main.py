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

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title="Smart Customer Support Agent",
    description="A FastAPI customer-support agent with tools, retrieval, persistence, and evals.",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(files_router)
app.include_router(sessions_router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/documents/{document_id}", include_in_schema=False)
def document_detail_page(document_id: str) -> FileResponse:
    return FileResponse(STATIC_DIR / "document.html")
