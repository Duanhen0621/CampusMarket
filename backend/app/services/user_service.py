from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import ProfileUpdate


def display_name(user: User) -> str:
    return user.nickname or user.student_id


def list_users(
    db: Session,
    page: int,
    size: int,
    keyword: str | None = None,
) -> tuple[int, list[User]]:
    stmt = select(User)
    if keyword:
        stmt = stmt.where(User.student_id.like(f"%{keyword}%"))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(User.id.asc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return total, list(rows)


def update_profile(
    db: Session, user: User, payload: ProfileUpdate
) -> User:
    data = payload.model_dump(exclude_unset=True)

    if "nickname" in data:
        user.nickname = (data.pop("nickname") or "").strip() or None
    if "phone" in data:
        user.phone = data.pop("phone")

    old_password = data.pop("old_password", None)
    new_password = data.pop("new_password", None)
    if new_password is not None:
        if not old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="修改密码请填写原密码",
            )
        if not verify_password(old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码不正确",
            )
        user.password = hash_password(new_password)
    elif old_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请填写新密码",
        )

    db.commit()
    db.refresh(user)
    return user


def revoke_admin(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )
    if user.role == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能撤销超级管理员",
        )
    if user.role != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户不是管理员",
        )
    user.role = 0
    db.commit()
    db.refresh(user)
    return user
