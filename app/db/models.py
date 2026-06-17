"""SQLAlchemy ORM 模型定义。

定义所有持久化实体：聊天会话、消息、文档、文档片段、工具调用记录、评测结果。
使用 SQLAlchemy 2.0 声明式映射风格。
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""
    pass


class ChatSession(Base):
    """聊天会话表：一次用户可见的完整对话。"""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(120), nullable=True)       # 会话标题（自动从首条消息生成）
    is_test: Mapped[bool] = mapped_column(Boolean, default=False)               # 标记测试/评测会话，侧边栏不展示
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # 级联关系：删除会话时自动清理关联的消息和工具调用
    messages: Mapped[list["Message"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    tool_calls: Mapped[list["ToolCall"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """消息表：会话中的一条用户或助手消息。"""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(32))       # "user" 或 "assistant"
    content: Mapped[str] = mapped_column(Text)          # 消息内容
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    session: Mapped[ChatSession] = relationship(back_populates="messages")


class Document(Base):
    """文档表：用户上传的知识库文档元数据。"""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), index=True)              # 原始文件名
    content_type: Mapped[str] = mapped_column(String(100), default="text/plain")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 一个文档被切分为多个可检索的片段
    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """文档片段表：从上传文档中提取的可检索文本块。

    RAG 检索的基本单元，每个片段关联一个源文档。
    """

    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(96), primary_key=True)               # 格式：{document_id}:{chunk_index}
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)                           # 片段在文档中的顺序索引
    content: Mapped[str] = mapped_column(Text)                                  # 片段文本内容
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    document: Mapped[Document] = relationship(back_populates="chunks")


class ToolCall(Base):
    """工具调用记录表：Agent 调用工具的输入输出，用于调试和流程追溯。"""

    __tablename__ = "tool_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    tool_name: Mapped[str] = mapped_column(String(80))      # 工具名称（calculator/search/retrieval）
    tool_input: Mapped[str] = mapped_column(Text)           # 工具输入参数
    tool_output: Mapped[str] = mapped_column(Text)          # 工具输出结果
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    session: Mapped[ChatSession] = relationship(back_populates="tool_calls")


class EvalRun(Base):
    """评测批次表：一次完整的评测运行记录。"""

    __tablename__ = "eval_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))          # 评测名称
    total: Mapped[int] = mapped_column(Integer, default=0)  # 总测试用例数
    passed: Mapped[int] = mapped_column(Integer, default=0) # 通过的用例数
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    results: Mapped[list["EvalResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class EvalResult(Base):
    """评测结果明细表：单个测试用例的详细结果。"""

    __tablename__ = "eval_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    eval_run_id: Mapped[int] = mapped_column(ForeignKey("eval_runs.id"), index=True)
    question: Mapped[str] = mapped_column(Text)                         # 测试问题
    expected_tool: Mapped[str] = mapped_column(String(80))              # 预期应调用的工具
    actual_tools: Mapped[str] = mapped_column(Text)                     # 实际调用的工具（逗号分隔）
    passed: Mapped[bool] = mapped_column(Boolean, default=False)        # 是否通过
    notes: Mapped[str] = mapped_column(Text, default="")                # 备注说明

    run: Mapped[EvalRun] = relationship(back_populates="results")
