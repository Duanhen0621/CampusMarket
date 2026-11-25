from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True, comment="学号（登录账号）"
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    nickname: Mapped[str | None] = mapped_column(
        String(50), comment="昵称（为空时显示学号）"
    )
    phone: Mapped[str | None] = mapped_column(String(20), comment="手机号")
    role: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0", comment="0=学生 1=管理员"
    )
    status: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1", comment="1=正常 0=封禁"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="注册时间"
    )
