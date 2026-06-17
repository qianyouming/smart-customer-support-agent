"""基于规则的 Agent 运行器。

核心职责：根据用户消息选择工具、构建上下文、生成回答、持久化对话轮次。
设计上刻意保持简单，使得 Agent/RAG 的执行流程清晰可审查。

执行流程：
1. 意图识别（规则匹配关键词）
2. 工具调用（计算器 / 文档检索 / 客服知识库搜索）
3. 上下文组装（历史消息 + 工具输出）
4. 答案生成（Mock 或真实 LLM）
5. 状态持久化（消息和工具调用写入数据库）
"""

import re

from app.agent.state import AgentState
from app.core.config import settings
from app.db.crud import add_message, add_tool_call
from app.llm.client import generate_answer
from app.schemas.chat import ChatResponse, Citation, ToolTrace
from app.tools import calculator, retrieval, search


# ============================================================
# 意图识别函数：通过关键词规则判断用户需要哪些工具
# ============================================================


def _looks_like_math(message: str) -> bool:
    """检测消息中是否包含可安全计算的算术表达式。"""
    return bool(calculator.extract_expression(message))


def _needs_retrieval(message: str) -> bool:
    """判断是否需要从用户上传的文档中检索上下文（RAG）。

    当用户提到"文档""知识库"等关键词时触发文档检索。
    """
    keywords = ["文档", "资料", "引用", "根据", "上传", "知识库", "knowledge", "document", "rag"]
    return any(keyword.lower() in message.lower() for keyword in keywords)


def _needs_search(message: str) -> bool:
    """判断是否需要搜索内置客服知识库（FAQ 式问答）。

    当用户问及退款、会员、价格等客服常见问题时触发。
    """
    keywords = ["退款", "会员", "价格", "客服", "售后", "订单", "agent", "rag", "搜索", "查一下"]
    return any(keyword.lower() in message.lower() for keyword in keywords)


def _asks_for_human(message: str) -> bool:
    """检测用户是否明确要求转接人工客服。"""
    keywords = ["人工", "真人", "客服", "转人工", "联系人员", "联系售后"]
    return any(keyword in message for keyword in keywords)


# ============================================================
# 辅助函数：处理工具输出、引用提取、持久化
# ============================================================


def _citation_from_retrieval_output(output: str) -> list[Citation]:
    """将检索工具返回的 '[来源] 片段' 格式文本解析为结构化引用列表。

    格式示例：
        [产品手册.pdf] 退款流程为3-5个工作日...
    """
    citations: list[Citation] = []
    for line in output.splitlines():
        match = re.match(r"\[(?P<source>.+?)\]\s(?P<snippet>.+)", line.strip())
        if match:
            citations.append(Citation(source=match.group("source"), snippet=match.group("snippet")))
    return citations


def _record_tool_calls(session_id: str, traces: list[ToolTrace]) -> None:
    """将工具调用记录持久化到数据库，便于 UI 展示和事后审计。"""
    for trace in traces:
        add_tool_call(
            session_id=session_id,
            tool_name=trace.tool_name,
            tool_input=trace.tool_input,
            tool_output=trace.tool_output,
        )


# ============================================================
# 核心入口：执行一轮完整的 Agent 对话
# ============================================================


def run_agent(message: str, state: AgentState) -> ChatResponse:
    """执行一轮聊天，返回结构化响应供前端渲染。

    整体逻辑：
    1. 保存用户消息到数据库
    2. 依次判断并执行相关工具（计算器 → 文档检索 → 客服搜索）
    3. 判断是否需要转人工
    4. 组装上下文并生成回答
    5. 更新内存状态和数据库
    6. 返回包含回答、工具追踪、引用等信息的响应体
    """
    used_tools: list[ToolTrace] = []
    citations: list[Citation] = []
    context_parts: list[str] = []
    retrieval_requested = _needs_retrieval(message)

    # 持久化用户消息
    add_message(state.session_id, "user", message)

    # --- 工具执行（确定性规则，保证演示和测试的可预测性） ---

    # 1) 计算器：处理算术表达式
    if _looks_like_math(message):
        expression = calculator.extract_expression(message) or message
        output = calculator.run(expression)
        used_tools.append(ToolTrace(tool_name="calculator", tool_input=expression, tool_output=output))
        context_parts.append(f"calculator result: {expression} = {output}")

    # 2) 文档检索（RAG）：从上传的文档中查找相关片段
    if retrieval_requested:
        output = retrieval.run(message)
        used_tools.append(ToolTrace(tool_name="retrieval", tool_input=message, tool_output=output))
        context_parts.append(output)
        citations.extend(_citation_from_retrieval_output(output))

    # 3) 客服知识库搜索：仅在没有文档引用时使用 FAQ 知识库
    if _needs_search(message) and not citations:
        output = search.run(message)
        used_tools.append(ToolTrace(tool_name="search", tool_input=message, tool_output=output))
        context_parts.append(output)

    # --- 人工介入判断 ---
    # 触发条件：用户明确要求 或 请求了文档检索但未找到任何引用
    need_human = _asks_for_human(message) or (retrieval_requested and not citations)
    handoff_reason = None
    if need_human:
        handoff_reason = "知识库证据不足或用户明确要求人工介入。"

    # --- 组装 LLM 上下文 ---
    recent_messages = state.messages[-settings.max_history_messages :]
    history = "\n".join(f"{item['role']}: {item['content']}" for item in recent_messages)
    context = "\n\n".join(part for part in [history, *context_parts] if part)

    # --- 生成回答 ---
    # 当用户要求文档证据但知识库无相关内容时，拒绝幻觉，建议转人工
    if need_human and retrieval_requested and not citations:
        answer = "当前知识库没有足够依据回答这个问题，建议转人工处理。"
    elif used_tools and used_tools[-1].tool_name == "calculator":
        # 计算器结果直接作为回答
        trace = used_tools[-1]
        answer = f"{trace.tool_input} = {trace.tool_output}"
    else:
        answer = generate_answer(message=message, context=context or None)

    # --- 更新状态和持久化 ---
    state.messages.append({"role": "user", "content": message})
    state.messages.append({"role": "assistant", "content": answer})
    state.tool_traces.extend(used_tools)

    add_message(state.session_id, "assistant", answer)
    _record_tool_calls(state.session_id, used_tools)

    return ChatResponse(
        answer=answer,
        session_id=state.session_id,
        used_tools=used_tools,
        citations=citations,
        need_human=need_human,
        handoff_reason=handoff_reason,
    )
