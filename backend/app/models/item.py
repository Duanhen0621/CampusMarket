from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, comment="发布者 ID"
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="标题")
    description: Mapped[str | None] = mapped_column(Text, comment="商品描述")
    type: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="1=出售 2=求购 3=交换"
    )
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), comment="期望价格")
    image_urls: Mapped[str | None] = mapped_column(
        String(500), comment="图片 URL，多图以 JSON 数组字符串存储"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        index=True,
        comment="0=待审核 1=展示中 2=已驳回 3=已下架",
    )
    reject_reason: Mapped[str | None] = mapped_column(
        String(255), comment="驳回原因（status=2 时有值）"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="发布时间"
    )
