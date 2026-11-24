from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AdminApplicationCreate(BaseModel):
    reason: str = Field(min_length=10, max_length=500)


class AdminApplicationReview(BaseModel):
    status: Literal[1, 2] = Field(description="1=通过 2=驳回")
    review_note: str | None = Field(default=None, max_length=255)


class AdminApplicationOut(BaseModel):
    id: int
    user_id: int
    reason: str
    status: int
    reviewer_id: int | None = None
    review_note: str | None = None
    created_at: datetime
    reviewed_at: datetime | None = None
    applicant_student_id: str | None = None
    reviewer_student_id: str | None = None
