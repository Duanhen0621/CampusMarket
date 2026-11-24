from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin_application import (
    AdminApplicationCreate,
    AdminApplicationOut,
)
from app.schemas.common import ApiResponse, PageData
from app.services import admin_application_service

router = APIRouter(prefix="/admin-applications", tags=["AdminApplication"])


@router.post(
    "", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED
)
def apply_for_admin(
    payload: AdminApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = admin_application_service.apply(
        db, current_user, payload.reason
    )
    return ApiResponse(
        code=status.HTTP_201_CREATED,
        msg="申请已提交，请等待超级管理员审批",
        data={"application_id": application.id},
    )


@router.get("/my", response_model=ApiResponse[PageData[AdminApplicationOut]])
def my_applications(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total, rows = admin_application_service.list_my(
        db, current_user, page, size
    )
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )
