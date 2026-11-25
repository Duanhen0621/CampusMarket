import json

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate
from app.services.publish_strategy import get_publish_strategy
from app.services.user_service import display_name


def load_image_urls(item: Item) -> list[str]:
    if not item.image_urls:
        return []
    try:
        value = json.loads(item.image_urls)
        if isinstance(value, list):
            return [str(url) for url in value]
    except (TypeError, ValueError):
        pass
    return [url.strip() for url in item.image_urls.split(",") if url.strip()]


def to_item_out(item: Item) -> ItemOut:
    urls = load_image_urls(item)
    return ItemOut(
        id=item.id,
        user_id=item.user_id,
        title=item.title,
        description=item.description,
        type=item.type,
        price=item.price,
        image_urls=urls,
        cover_url=urls[0] if urls else None,
        publisher_display_name=(
            display_name(item.owner) if item.owner is not None else None
        ),
        status=item.status,
        reject_reason=item.reject_reason,
        created_at=item.created_at,
    )


def _paginate(db: Session, stmt, page: int, size: int, descending: bool = True):
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    order = Item.created_at.desc() if descending else Item.created_at.asc()
    rows = db.scalars(
        stmt.order_by(order).offset((page - 1) * size).limit(size)
    ).all()
    return total, [to_item_out(item) for item in rows]


def list_public_items(
    db: Session,
    page: int,
    size: int,
    keyword: str | None = None,
    item_type: int | None = None,
):
    stmt = select(Item).where(Item.status == 1)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            or_(Item.title.like(like), Item.description.like(like))
        )
    if item_type:
        stmt = stmt.where(Item.type == item_type)
    return _paginate(db, stmt, page, size)


def list_user_items(
    db: Session,
    user_id: int,
    page: int,
    size: int,
    item_status: int | None = None,
):
    stmt = select(Item).where(Item.user_id == user_id)
    if item_status is not None:
        stmt = stmt.where(Item.status == item_status)
    return _paginate(db, stmt, page, size)


def list_pending_items(db: Session, page: int, size: int):
    stmt = select(Item).where(Item.status == 0)
    return _paginate(db, stmt, page, size, descending=False)


def get_item_or_404(db: Session, item_id: int) -> Item:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在"
        )
    return item


def get_public_item(db: Session, item_id: int) -> ItemOut:
    item = get_item_or_404(db, item_id)
    if item.status != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在或未通过审核"
        )
    return to_item_out(item)


def get_owned_item(db: Session, item_id: int, user: User) -> Item:
    item = get_item_or_404(db, item_id)
    if item.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权操作该商品"
        )
    return item


def create_item(db: Session, user: User, payload: ItemCreate) -> Item:
    get_publish_strategy(payload.type).validate(payload)
    item = Item(
        user_id=user.id,
        title=payload.title,
        description=payload.description,
        type=payload.type,
        price=payload.price,
        image_urls=json.dumps(payload.image_urls, ensure_ascii=False),
        status=0,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item: Item, payload: ItemUpdate) -> Item:
    data = payload.model_dump(exclude_unset=True)
    if "image_urls" in data:
        data["image_urls"] = json.dumps(
            data["image_urls"] or [], ensure_ascii=False
        )
    for field, value in data.items():
        setattr(item, field, value)
    # 修改后重新进入审核流程
    item.status = 0
    item.reject_reason = None
    db.commit()
    db.refresh(item)
    return item


def off_shelf_item(db: Session, item: Item) -> Item:
    item.status = 3
    db.commit()
    db.refresh(item)
    return item
