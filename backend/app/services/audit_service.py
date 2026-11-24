"""管理员审核与举报处理业务（见设计说明书 4.1 / 4.5）。"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.user import User
from app.services.report_service import handle_report as handle_report_service


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_pending_item(self, item_id: int) -> Item:
        item = self.db.get(Item, item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在"
            )
        if item.status != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该商品不在待审核状态",
            )
        return item

    def approve_item(self, item_id: int) -> Item:
        item = self._get_pending_item(item_id)
        item.status = 1
        item.reject_reason = None
        self.db.commit()
        self.db.refresh(item)
        return item

    def reject_item(self, item_id: int, reason: str) -> Item:
        reason = (reason or "").strip()
        if not reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驳回商品时必须填写原因",
            )
        item = self._get_pending_item(item_id)
        item.status = 2
        item.reject_reason = reason
        self.db.commit()
        self.db.refresh(item)
        return item

    def set_user_status(self, user_id: int, new_status: int) -> User:
        if new_status not in (0, 1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="无效的用户状态"
            )
        user = self.db.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )
        if user.role >= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能封禁或解封管理员账号",
            )
        user.status = new_status
        self.db.commit()
        self.db.refresh(user)
        return user

    def ban_user(self, user_id: int) -> User:
        return self.set_user_status(user_id, 0)

    def handle_report(
        self,
        report_id: int,
        new_status: int,
        note: str | None,
        handler: User,
    ):
        return handle_report_service(
            self.db, handler, report_id, new_status, note
        )
