"""健康检查端点，前端在线状态指示器使用。"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """返回最简存活响应，表示服务正常运行。"""
    return {"status": "ok"}
