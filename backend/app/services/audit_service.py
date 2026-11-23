"""管理员审核与举报处理业务（见设计说明书 4.1 / 4.5）。"""

from sqlalchemy.orm import Session


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def approve_item(self, item_id: int) -> None:
        raise NotImplementedError("商品审核通过逻辑待实现")

    def reject_item(self, item_id: int, reason: str) -> None:
        raise NotImplementedError("商品驳回逻辑待实现（写入 reject_reason）")

    def ban_user(self, user_id: int) -> None:
        raise NotImplementedError("用户封禁逻辑待实现")

    def handle_report(self, report_id: int, status: int, note: str | None) -> None:
        raise NotImplementedError("举报处理逻辑待实现")
