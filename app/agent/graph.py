"""Agent 概念图描述模块。

当前实现采用轻量级的规则驱动方式。本文件记录了未来迁移到
LangGraph 风格有向图架构时的预期工作流程。
"""

from typing import TypedDict


class AgentGraphState(TypedDict, total=False):
    """Agent 工作流图的状态字段定义（为未来图架构预留）。

    Attributes:
        question: 用户原始问题
        rewritten_question: 经过改写优化后的查询
        retrieved_context: RAG 检索到的上下文
        answer: 最终生成的回答
    """

    question: str
    rewritten_question: str
    retrieved_context: str
    answer: str


def describe_graph() -> list[str]:
    """返回 Agent 工作流的高层级执行步骤（按顺序）。

    流程说明：
    1. rewrite_query    - 查询改写，优化检索效果
    2. retrieve_docs    - 从知识库检索相关文档片段
    3. decide_tool      - 判断是否需要调用工具（计算器/搜索等）
    4. generate_answer  - 结合上下文生成最终回答
    5. attach_citations - 附加引用来源信息
    """
    return [
        "rewrite_query",
        "retrieve_docs",
        "decide_tool",
        "generate_answer",
        "attach_citations",
    ]
