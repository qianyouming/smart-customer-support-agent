"""聊天请求和响应的 Pydantic 数据模型。

定义 API 层的数据契约，同时用于请求验证和响应序列化。
"""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """引用来源：RAG 回答时附带的文档片段引用。

    Attributes:
        source: 来源文件名
        snippet: 引用的文本片段
    """

    source: str
    snippet: str


class ToolTrace(BaseModel):
    """工具调用追踪：UI 中展示的单次工具调用详情。

    Attributes:
        tool_name: 工具名称（calculator/search/retrieval）
        tool_input: 输入参数
        tool_output: 输出结果
    """

    tool_name: str
    tool_input: str
    tool_output: str


class ChatRequest(BaseModel):
    """前端发送的聊天请求。

    Attributes:
        message: 用户消息（不能为空）
        session_id: 会话 ID（可选，未提供时自动生成）
    """

    message: str = Field(..., min_length=1)
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Agent 返回的结构化响应，供前端渲染完整的对话卡片。

    Attributes:
        answer: 生成的回答文本
        session_id: 会话 ID
        used_tools: 本轮使用的工具列表（展示在调试面板）
        citations: 引用来源列表（RAG 场景）
        need_human: 是否需要转人工处理
        handoff_reason: 转人工的原因说明
    """

    answer: str
    session_id: str
    used_tools: list[ToolTrace] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    need_human: bool = False
    handoff_reason: str | None = None
