from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    target_type: Literal[1, 2] = Field(description="1=商品 2=用户")
    target_id: int
    reason: str = Field(min_length=1, max_length=255)


class ReportHandleRequest(BaseModel):
    status: Literal[1, 2] = Field(description="1=属实（已处理） 2=不属实（已驳回）")
    handle_note: str | None = Field(default=None, max_length=255)


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporter_id: int
    target_type: int
    target_id: int
    reason: str
    status: int
    handler_id: int | None = None
    handle_note: str | None = None
    created_at: datetime
    handled_at: datetime | None = None

    reporter_student_id: str | None = None
    target_label: str | None = None
