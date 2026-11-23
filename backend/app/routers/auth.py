from fastapi import APIRouter, status

from app.core.stubs import not_implemented
from app.schemas.auth import LoginRequest, RegisterRequest, TokenData, UserOut
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["Auth/User"])


@router.post(
    "/register", response_model=ApiResponse[UserOut], status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest):
    not_implemented("用户注册")


@router.post("/login", response_model=ApiResponse[TokenData])
def login(payload: LoginRequest):
    not_implemented("用户登录")
