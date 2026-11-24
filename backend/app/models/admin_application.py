from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdminApplication(Base):
    __tablename__ = "admin_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, comment="申请人 ID"
    )
    reason: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="申请理由"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        index=True,
        comment="0=待审批 1=已通过 2=已驳回",
    )
    reviewer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), comment="审批人 ID"
    )
    review_note: Mapped[str | None] = mapped_column(
        String(255), comment="审批备注"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="申请时间"
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime, comment="审批时间"
    )
