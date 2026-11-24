from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_admin, require_super_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin_application import (
    AdminApplicationOut,
    AdminApplicationReview,
)
from app.schemas.common import ApiResponse, PageData
from app.schemas.item import ItemAuditRequest, ItemOut
from app.schemas.report import ReportHandleRequest, ReportOut
from app.services import admin_application_service, item_service, report_service
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


@router.get(
    "/applications",
    response_model=ApiResponse[PageData[AdminApplicationOut]],
    dependencies=[Depends(require_super_admin)],
)
def list_admin_applications(
    status: int | None = Query(None, ge=0, le=2),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    total, rows = admin_application_service.list_for_admin(
        db, page, size, status
    )
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )


@router.put("/applications/{application_id}", response_model=ApiResponse[dict])
def review_admin_application(
    application_id: int,
    payload: AdminApplicationReview,
    db: Session = Depends(get_db),
    admin: User = Depends(require_super_admin),
):
    application = admin_application_service.review(
        db, admin, application_id, payload.status, payload.review_note
    )
    return ApiResponse(
        msg="申请已通过" if payload.status == 1 else "申请已驳回",
        data={
            "application_id": application.id,
            "status": application.status,
        },
    )


@router.get("/reports", response_model=ApiResponse[PageData[ReportOut]])
def list_reports(
    status: int | None = Query(None, ge=0, le=2),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    total, rows = report_service.list_reports(db, page, size, status)
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )


@router.put("/reports/{report_id}", response_model=ApiResponse[dict])
def handle_report(
    report_id: int,
    payload: ReportHandleRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    report = AuditService(db).handle_report(
        report_id, payload.status, payload.handle_note, admin
    )
    return ApiResponse(
        msg="举报处理成功",
        data={"report_id": report.id, "status": report.status},
    )
