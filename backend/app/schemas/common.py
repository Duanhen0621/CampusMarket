from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应结构：{ code, msg, data }。"""

    code: int = 200
    msg: str = "success"
    data: T | None = None


class PageData(BaseModel, Generic[T]):
    total: int = 0
    page: int = 1
    size: int = 10
    list: List[T] = []
