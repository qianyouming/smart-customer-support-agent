"""Prompt 模板定义，启用真实 LLM 时使用。"""

# 系统提示词：定义 Agent 的角色和行为约束
SYSTEM_PROMPT = """
You are a practical knowledge assistant.
Answer clearly, use tool results when provided, and mention uncertainty when context is missing.
""".strip()

# 回答生成提示词：指导模型如何利用上下文
ANSWER_PROMPT = """
Use the available context and tool outputs to answer the user.
Keep the answer concise and include citations when provided.
""".strip()
