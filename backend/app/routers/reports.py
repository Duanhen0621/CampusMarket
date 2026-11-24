from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PageData
from app.schemas.report import ReportCreate, ReportOut
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["Report"])


@router.post(
    "", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED
)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = report_service.create_report(db, current_user, payload)
    return ApiResponse(
        code=status.HTTP_201_CREATED,
        msg="举报已提交，请等待管理员处理",
        data={"report_id": report.id},
    )


@router.get("/my", response_model=ApiResponse[PageData[ReportOut]])
def my_reports(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total, rows = report_service.list_my_reports(
        db, current_user, page, size
    )
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )
