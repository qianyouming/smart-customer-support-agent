"""微型客服知识库搜索工具（Mock 实现）。

用于演示和测试，替代真实的外部搜索服务，保证行为确定性。
生产环境可替换为 Elasticsearch、向量数据库等实现。
"""

# 工具 Schema 定义
TOOL_SCHEMA = {
    "type": "function",
    "name": "search",
    "description": "Search a tiny mock customer-support knowledge base.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"],
    },
}

# 模拟客服知识库：关键词 → 标准回复
KB = {
    "退款": "标准退款周期为 3-5 个工作日，原路退回。",
    "退货": "未使用且不影响二次销售的商品支持 7 天无理由退货。",
    "会员": "会员支持月付和年付两种方案，年付会有折扣。",
    "取消会员": "用户可以在账户设置中取消自动续费，已支付周期仍可继续使用。",
    "价格": "基础版 99 元/月，高级版 299 元/月，企业版需要联系销售。",
    "客服": "如果知识库证据不足，系统会建议转人工客服处理。",
    "agent": "Agent 应用通常由模型、工具、状态、记忆和评测组成。",
    "rag": "RAG 会先检索相关资料，再把资料作为上下文交给模型回答。",
}


def run(query: str) -> str:
    """从模拟知识库中查找第一个匹配关键词的回答。

    匹配逻辑：遍历 KB 字典，返回第一个关键词出现在 query 中的回复。
    若无匹配则建议转人工处理。
    """
    for keyword, answer in KB.items():
        if keyword.lower() in query.lower():
            return answer
    return "未在客服知识库中找到相关信息，建议转人工处理。"
