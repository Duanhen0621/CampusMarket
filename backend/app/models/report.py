from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_target", "target_type", "target_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reporter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, comment="举报人 ID"
    )
    target_type: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="1=商品 2=用户"
    )
    target_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="被举报对象 ID（多态，按 target_type 指向 items/users）"
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=False, comment="举报原因")
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="0=待处理 1=已处理/属实 2=已驳回/不属实",
    )
    handler_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), index=True, comment="处理管理员 ID"
    )
    handle_note: Mapped[str | None] = mapped_column(String(255), comment="处理备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="举报时间"
    )
    handled_at: Mapped[datetime | None] = mapped_column(DateTime, comment="处理时间")
