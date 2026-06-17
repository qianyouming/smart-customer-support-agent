"""LLM 客户端封装模块。

项目默认使用 Mock 响应，无需 API 密钥即可运行和测试。
当设置 USE_REAL_LLM=true 并配置 API 密钥后，会调用 OpenAI 兼容的
Chat Completions 接口（支持各种国产模型代理）。
"""

from app.core.config import settings
from app.llm.prompts import SYSTEM_PROMPT


def has_real_llm() -> bool:
    """判断是否应使用真实模型调用（需同时启用开关和配置密钥）。"""
    return settings.use_real_llm and bool(settings.openai_api_key)


def _mock_answer(message: str, context: str | None = None) -> str:
    """确定性的模拟回答，用于本地演示和自动化测试。

    根据关键词匹配返回预设回复，确保测试结果可预测。
    """
    lowered = message.lower()
    if "退款" in message:
        return "标准退款周期为 3-5 个工作日，通常会原路退回。"
    if "rag" in lowered:
        return "RAG 是检索增强生成：系统先检索相关资料，再把资料作为上下文交给模型生成回答。"
    if "人工" in message or "转人工" in message:
        return "已为你标记人工介入需求，客服人员可以继续跟进。"
    if context:
        return f"我已参考当前可用信息回答：{message}"
    return f"[mock] 你刚刚说的是：{message}"


def generate_answer(message: str, context: str | None = None) -> str:
    """生成回答的统一入口：自动选择 Mock 或真实 LLM。

    Args:
        message: 用户当前消息
        context: 组装好的上下文（历史对话 + 工具输出）

    Returns:
        生成的回答文本
    """
    if not has_real_llm():
        return _mock_answer(message=message, context=context)

    # 延迟导入 openai，仅在真正需要时加载（避免未安装时报错）
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    # 将上下文拼接到用户输入中，让模型能参考工具结果和历史对话
    user_input = message if not context else f"Context:\n{context}\n\nUser question:\n{message}"
    response = client.chat.completions.create(
        model=settings.model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content or ""
