from app.core.config import settings
from app.llm.prompts import SYSTEM_PROMPT


def has_real_llm() -> bool:
    return settings.use_real_llm and bool(settings.openai_api_key)


def _mock_answer(message: str, context: str | None = None) -> str:
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
    if not has_real_llm():
        return _mock_answer(message=message, context=context)

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    user_input = message if not context else f"Context:\n{context}\n\nUser question:\n{message}"
    response = client.chat.completions.create(
        model=settings.model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content or ""
