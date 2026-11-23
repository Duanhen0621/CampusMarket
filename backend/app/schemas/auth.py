from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    student_id: str = Field(min_length=4, max_length=20, description="学号")
    password: str = Field(min_length=6, max_length=64)
    phone: str | None = Field(default=None, max_length=20)


class LoginRequest(BaseModel):
    student_id: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: str
    phone: str | None = None
    role: int = 0
    status: int = 1


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
