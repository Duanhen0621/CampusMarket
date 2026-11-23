from fastapi import APIRouter, Query, status

from app.core.stubs import not_implemented
from app.schemas.common import ApiResponse, PageData
from app.schemas.report import ReportCreate, ReportOut

router = APIRouter(prefix="/reports", tags=["Report"])


@router.post("", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate):
    not_implemented("提交举报")


@router.get("/my", response_model=ApiResponse[PageData[ReportOut]])
def my_reports(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    not_implemented("我的举报")
