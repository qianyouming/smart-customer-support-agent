"""Rule-based Agent runner.

The runner selects tools, builds context, generates an answer, and persists the
turn. It deliberately stays simple so the Agent/RAG flow is easy to inspect.
"""

import re

from app.agent.state import AgentState
from app.core.config import settings
from app.db.crud import add_message, add_tool_call
from app.llm.client import generate_answer
from app.schemas.chat import ChatResponse, Citation, ToolTrace
from app.tools import calculator, retrieval, search


def _looks_like_math(message: str) -> bool:
    """Detect whether the message contains a safe arithmetic expression."""
    return bool(calculator.extract_expression(message))


def _needs_retrieval(message: str) -> bool:
    """Decide whether uploaded documents should be searched for context."""
    keywords = ["文档", "资料", "引用", "根据", "上传", "知识库", "knowledge", "document", "rag"]
    return any(keyword.lower() in message.lower() for keyword in keywords)


def _needs_search(message: str) -> bool:
    """Decide whether the mock customer-support KB should be searched."""
    keywords = ["退款", "会员", "价格", "客服", "售后", "订单", "agent", "rag", "搜索", "查一下"]
    return any(keyword.lower() in message.lower() for keyword in keywords)


def _asks_for_human(message: str) -> bool:
    """Detect explicit user intent to transfer to a human support agent."""
    keywords = ["人工", "真人", "客服", "转人工", "联系人员", "联系售后"]
    return any(keyword in message for keyword in keywords)


def _citation_from_retrieval_output(output: str) -> list[Citation]:
    """Convert retrieval output formatted as '[source] snippet' into citations."""
    citations: list[Citation] = []
    for line in output.splitlines():
        match = re.match(r"\[(?P<source>.+?)\]\s(?P<snippet>.+)", line.strip())
        if match:
            citations.append(Citation(source=match.group("source"), snippet=match.group("snippet")))
    return citations


def _record_tool_calls(session_id: str, traces: list[ToolTrace]) -> None:
    """Store tool traces so the UI and database can explain what happened."""
    for trace in traces:
        add_tool_call(
            session_id=session_id,
            tool_name=trace.tool_name,
            tool_input=trace.tool_input,
            tool_output=trace.tool_output,
        )


def run_agent(message: str, state: AgentState) -> ChatResponse:
    """Run one chat turn and return a structured response for the frontend."""
    used_tools: list[ToolTrace] = []
    citations: list[Citation] = []
    context_parts: list[str] = []
    retrieval_requested = _needs_retrieval(message)

    add_message(state.session_id, "user", message)

    # Tool execution is deterministic here, which keeps the demo testable.
    if _looks_like_math(message):
        expression = calculator.extract_expression(message) or message
        output = calculator.run(expression)
        used_tools.append(ToolTrace(tool_name="calculator", tool_input=expression, tool_output=output))
        context_parts.append(f"calculator result: {expression} = {output}")

    if retrieval_requested:
        output = retrieval.run(message)
        used_tools.append(ToolTrace(tool_name="retrieval", tool_input=message, tool_output=output))
        context_parts.append(output)
        citations.extend(_citation_from_retrieval_output(output))

    if _needs_search(message) and not citations:
        output = search.run(message)
        used_tools.append(ToolTrace(tool_name="search", tool_input=message, tool_output=output))
        context_parts.append(output)

    need_human = _asks_for_human(message) or (retrieval_requested and not citations)
    handoff_reason = None
    if need_human:
        handoff_reason = "知识库证据不足或用户明确要求人工介入。"

    recent_messages = state.messages[-settings.max_history_messages :]
    history = "\n".join(f"{item['role']}: {item['content']}" for item in recent_messages)
    context = "\n\n".join(part for part in [history, *context_parts] if part)

    # Avoid hallucinating when the user explicitly requested document evidence.
    if need_human and retrieval_requested and not citations:
        answer = "当前知识库没有足够依据回答这个问题，建议转人工处理。"
    elif used_tools and used_tools[-1].tool_name == "calculator":
        trace = used_tools[-1]
        answer = f"{trace.tool_input} = {trace.tool_output}"
    else:
        answer = generate_answer(message=message, context=context or None)

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
