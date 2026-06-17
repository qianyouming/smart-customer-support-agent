"""日志工具模块，为各模块提供统一的命名日志器。"""

import logging


def get_logger(name: str) -> logging.Logger:
    """配置基础日志格式并返回指定名称的日志器。

    Args:
        name: 日志器名称，通常传入模块的 __name__

    Returns:
        配置好的 Logger 实例
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    return logging.getLogger(name)
