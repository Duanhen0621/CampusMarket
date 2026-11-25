from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.services import user_service
from app.schemas.auth import (
    LoginRequest,
    ProfileUpdate,
    RegisterRequest,
    TokenData,
    UserOut,
)
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["Auth/User"])


@router.post(
    "/register", response_model=ApiResponse[UserOut], status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.student_id == payload.student_id))
    if exists is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该学号已注册")

    user = User(
        student_id=payload.student_id,
        password=hash_password(payload.password),
        nickname=(payload.nickname or "").strip() or None,
        phone=payload.phone,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该学号已注册"
        ) from None
    db.refresh(user)

    return ApiResponse(
        code=status.HTTP_201_CREATED,
        msg="注册成功",
        data=UserOut.model_validate(user),
    )


@router.post("/login", response_model=ApiResponse[TokenData])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.student_id == payload.student_id))
    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="学号或密码错误"
        )
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已被封禁"
        )

    token = create_access_token(str(user.id))
    return ApiResponse(
        msg="登录成功",
        data=TokenData(
            access_token=token,
            user=UserOut.model_validate(user),
        ),
    )


@router.get("/me", response_model=ApiResponse[UserOut])
def me(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=UserOut.model_validate(current_user))


@router.put("/me", response_model=ApiResponse[UserOut])
def update_me(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.update_profile(db, current_user, payload)
    return ApiResponse(msg="资料已更新", data=UserOut.model_validate(user))
