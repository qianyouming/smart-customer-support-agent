"""通用 API 数据模型。"""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """统一错误响应格式。"""

    error: str
