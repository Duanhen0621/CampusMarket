from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.item import Item
from app.models.message import Message
from app.models.user import User
from app.schemas.interaction import MessageOut
from app.schemas.item import ItemOut
from app.services.item_service import to_item_out
from app.services.user_service import display_name


def _get_public_item(db: Session, item_id: int) -> Item:
    item = db.get(Item, item_id)
    if item is None or item.status != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在或未通过审核"
        )
    return item


def list_messages(
    db: Session, item_id: int, page: int, size: int
) -> tuple[int, list[MessageOut]]:
    _get_public_item(db, item_id)
    total = db.scalar(
        select(func.count()).select_from(Message).where(Message.item_id == item_id)
    ) or 0
    rows = db.execute(
        select(Message, User.nickname, User.student_id)
        .join(User, Message.user_id == User.id)
        .where(Message.item_id == item_id)
        .order_by(Message.created_at.asc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return total, [
        MessageOut(
            id=message.id,
            item_id=message.item_id,
            user_id=message.user_id,
            student_id=student_id,
            display_name=nickname or student_id,
            content=message.content,
            created_at=message.created_at,
        )
        for message, nickname, student_id in rows
    ]


def create_message(
    db: Session, user: User, item_id: int, content: str
) -> MessageOut:
    _get_public_item(db, item_id)
    content = content.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="留言内容不能为空"
        )
    message = Message(item_id=item_id, user_id=user.id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return MessageOut(
        id=message.id,
        item_id=message.item_id,
        user_id=message.user_id,
        student_id=user.student_id,
        display_name=display_name(user),
        content=message.content,
        created_at=message.created_at,
    )


def add_favorite(db: Session, user: User, item_id: int) -> Favorite:
    _get_public_item(db, item_id)
    existing = db.scalar(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.item_id == item_id
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="已收藏该商品"
        )
    favorite = Favorite(user_id=user.id, item_id=item_id)
    db.add(favorite)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="已收藏该商品"
        ) from None
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, user: User, item_id: int) -> None:
    favorite = db.scalar(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.item_id == item_id
        )
    )
    if favorite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="尚未收藏该商品"
        )
    db.delete(favorite)
    db.commit()


def is_favorited(db: Session, user_id: int, item_id: int) -> bool:
    return (
        db.scalar(
            select(Favorite.id).where(
                Favorite.user_id == user_id, Favorite.item_id == item_id
            )
        )
        is not None
    )


def list_favorites(
    db: Session, user_id: int, page: int, size: int
) -> tuple[int, list[ItemOut]]:
    total = db.scalar(
        select(func.count()).select_from(Favorite).where(Favorite.user_id == user_id)
    ) or 0
    rows = db.scalars(
        select(Item)
        .join(Favorite, Favorite.item_id == Item.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return total, [to_item_out(item) for item in rows]
