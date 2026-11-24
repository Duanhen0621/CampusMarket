from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    item_id: int


class OrderStatusUpdate(BaseModel):
    status: Literal[0, 1, 2, 3] = Field(
        description="0=待确认 1=交易中 2=已完成 3=已取消"
    )


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    buyer_id: int
    seller_id: int
    status: int
    created_at: datetime

    item_title: str | None = None
    item_cover_url: str | None = None
    buyer_student_id: str | None = None
    seller_student_id: str | None = None
