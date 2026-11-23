from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id"), nullable=False, index=True, comment="商品 ID"
    )
    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, comment="买家 ID"
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, comment="卖家 ID"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="0=待确认 1=交易中 2=已完成 3=已取消",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="订单创建时间"
    )
