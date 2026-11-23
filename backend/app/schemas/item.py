from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None
    type: Literal[1, 2, 3] = Field(description="1=出售 2=求购 3=交换")
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    image_urls: list[str] = Field(default_factory=list, max_length=9)


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    image_urls: list[str] | None = Field(default=None, max_length=9)


class ItemAuditRequest(BaseModel):
    status: Literal[1, 2] = Field(description="1=通过 2=驳回")
    reason: str | None = Field(default=None, max_length=255)


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None = None
    type: int
    price: Decimal | None = None
    image_urls: str | None = None
    status: int
    reject_reason: str | None = None
    created_at: datetime
