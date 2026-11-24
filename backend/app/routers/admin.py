from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.core.stubs import not_implemented
from app.db.session import get_db
from app.schemas.common import ApiResponse, PageData
from app.schemas.item import ItemAuditRequest, ItemOut
from app.schemas.report import ReportHandleRequest, ReportOut
from app.services import item_service
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)]
)


@router.get("/items/pending", response_model=ApiResponse[PageData[ItemOut]])
def pending_items(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    total, rows = item_service.list_pending_items(db, page, size)
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )


@router.put("/items/{item_id}/audit", response_model=ApiResponse[dict])
def audit_item(
    item_id: int,
    payload: ItemAuditRequest,
    db: Session = Depends(get_db),
):
    service = AuditService(db)
    if payload.status == 1:
        item = service.approve_item(item_id)
        msg = "审核通过"
    else:
        item = service.reject_item(item_id, payload.reason or "")
        msg = "已驳回"
    return ApiResponse(
        msg=msg, data={"item_id": item.id, "status": item.status}
    )


@router.put("/users/{user_id}/ban", response_model=ApiResponse[dict])
def ban_user(user_id: int, db: Session = Depends(get_db)):
    user = AuditService(db).ban_user(user_id)
    return ApiResponse(
        msg="用户已封禁", data={"user_id": user.id, "status": user.status}
    )


@router.get("/reports", response_model=ApiResponse[PageData[ReportOut]])
def list_reports(
    status: int | None = Query(None, ge=0, le=2),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    not_implemented("举报工单列表")


@router.put("/reports/{report_id}", response_model=ApiResponse[dict])
def handle_report(report_id: int, payload: ReportHandleRequest):
    not_implemented("处理举报")
