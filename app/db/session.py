"""数据库引擎、会话工厂，以及轻量级 SQLite 迁移。

使用 SQLAlchemy 管理数据库连接，支持 SQLite（默认）和其他数据库。
包含简单的 schema 迁移逻辑，处理表结构变更。
"""

from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.models import Base


def _ensure_sqlite_parent() -> None:
    """确保 SQLite 数据库文件的父目录存在。

    SQLite 不会自动创建目录，需要提前准备。
    """
    if not settings.database_url.startswith("sqlite:///"):
        return
    raw_path = settings.database_url.replace("sqlite:///", "", 1)
    Path(raw_path).parent.mkdir(parents=True, exist_ok=True)


# 模块加载时即确保目录存在
_ensure_sqlite_parent()

# SQLite 需要 check_same_thread=False 以支持多线程访问
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """创建所有表并执行兼容性迁移。应用启动时调用一次。"""
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_sessions()


def get_db_session() -> Session:
    """返回一个新的 SQLAlchemy 会话，确保 schema 已就绪。"""
    init_db()
    return SessionLocal()


def _migrate_sqlite_sessions() -> None:
    """为初始演示数据库添加后续引入的新字段。

    SQLite 不支持完整的 ALTER TABLE，这里逐列检查并添加缺失的列。
    这是一个简易迁移方案，生产环境建议使用 Alembic。
    """
    if not settings.database_url.startswith("sqlite"):
        return
    inspector = inspect(engine)
    if "sessions" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("sessions")}
    with engine.begin() as conn:
        if "title" not in columns:
            conn.execute(text("ALTER TABLE sessions ADD COLUMN title VARCHAR(120)"))
        if "is_test" not in columns:
            conn.execute(text("ALTER TABLE sessions ADD COLUMN is_test BOOLEAN DEFAULT 0"))
