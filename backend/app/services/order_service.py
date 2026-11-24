from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models.item import Item
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderOut
from app.services.item_service import load_image_urls

ACTIVE_STATUSES = (0, 1)


def create_order(db: Session, user: User, item_id: int) -> Order:
    item = db.get(Item, item_id)
    if item is None or item.status != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在或未上架"
        )
    if item.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不能购买自己发布的商品"
        )

    active = db.scalar(
        select(Order.id).where(
            Order.item_id == item_id, Order.status.in_(ACTIVE_STATUSES)
        )
    )
    if active is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该商品已有进行中的订单",
        )

    # 求购商品由发布者充当买家，发起者充当卖家
    if item.type == 2:
        buyer_id, seller_id = item.user_id, user.id
    else:
        buyer_id, seller_id = user.id, item.user_id

    order = Order(
        item_id=item_id,
        buyer_id=buyer_id,
        seller_id=seller_id,
        status=0,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def list_my_orders(
    db: Session, user_id: int, page: int, size: int
) -> tuple[int, list[OrderOut]]:
    buyer = aliased(User)
    seller = aliased(User)

    condition = or_(Order.buyer_id == user_id, Order.seller_id == user_id)
    total = db.scalar(
        select(func.count()).select_from(Order).where(condition)
    ) or 0

    rows = db.execute(
        select(Order, Item, buyer.student_id, seller.student_id)
        .join(Item, Order.item_id == Item.id)
        .join(buyer, Order.buyer_id == buyer.id)
        .join(seller, Order.seller_id == seller.id)
        .where(condition)
        .order_by(Order.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    result = []
    for order, item, buyer_student_id, seller_student_id in rows:
        urls = load_image_urls(item)
        result.append(
            OrderOut(
                id=order.id,
                item_id=order.item_id,
                buyer_id=order.buyer_id,
                seller_id=order.seller_id,
                status=order.status,
                created_at=order.created_at,
                item_title=item.title,
                item_cover_url=urls[0] if urls else None,
                buyer_student_id=buyer_student_id,
                seller_student_id=seller_student_id,
            )
        )
    return total, result


def update_status(
    db: Session, user: User, order_id: int, new_status: int
) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在"
        )
    if user.id not in (order.buyer_id, order.seller_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权操作该订单"
        )
    if order.status in (2, 3):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="订单已结束，不能修改"
        )
    if new_status == order.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="订单状态未变化"
        )

    if new_status == 3:  # 取消订单：买卖双方均可
        pass
    elif new_status == 1:  # 确认交易：仅卖家
        if order.status != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有待确认的订单可以确认交易",
            )
        if user.id != order.seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有卖家可以确认订单",
            )
    elif new_status == 2:  # 完成交易：交易中的订单，买卖双方均可
        if order.status != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有交易中的订单可以完成",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的状态流转"
        )

    order.status = new_status
    if new_status == 2:
        item = db.get(Item, order.item_id)
        if item is not None:
            item.status = 3

    db.commit()
    db.refresh(order)
    return order
