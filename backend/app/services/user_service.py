from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import ProfileUpdate


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
    if "phone" in data:
        user.phone = data["phone"]
    db.commit()
    db.refresh(user)
    return user
