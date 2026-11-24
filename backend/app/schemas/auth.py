from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    student_id: str = Field(min_length=4, max_length=20, description="学号")
    password: str = Field(min_length=6, max_length=64)
    phone: str | None = Field(default=None, max_length=20)


class LoginRequest(BaseModel):
    student_id: str
    password: str


class ProfileUpdate(BaseModel):
    phone: str | None = Field(default=None, max_length=20)


class UserStatusUpdate(BaseModel):
    status: Literal[0, 1] = Field(description="0=封禁 1=正常")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: str
    phone: str | None = None
    role: int = 0
    status: int = 1
    created_at: datetime | None = None


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
