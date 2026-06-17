"""应用配置模块，从环境变量和 .env 文件加载设置。

所有可配置项集中管理，各模块通过导入 settings 单例访问。
支持 OpenAI 兼容接口、数据库路径、RAG 参数等配置。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置对象，供 API、数据库、RAG 和 LLM 模块统一使用。

    配置优先级：环境变量 > .env 文件 > 默认值
    """

    # LLM 相关配置
    openai_api_key: str | None = None           # OpenAI 兼容 API 密钥
    openai_base_url: str | None = None          # 自定义 API 端点（支持国产模型代理）
    use_real_llm: bool = False                  # 是否启用真实 LLM，False 时使用 mock 响应
    model: str = "gpt-4.1-mini"                 # 使用的模型名称

    # 应用运行配置
    debug: bool = True                          # 调试模式开关
    data_dir: str = "data"                      # 数据文件存储目录

    # 数据库配置
    database_url: str = "sqlite:///data/knowledge_agent.db"  # SQLite 数据库路径

    # Agent 行为参数
    max_history_messages: int = 8               # 传递给 LLM 的最大历史消息数
    top_k_chunks: int = 3                       # RAG 检索时返回的最相关片段数

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# 全局配置单例，整个应用共享
settings = Settings()
