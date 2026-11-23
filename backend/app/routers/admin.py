from fastapi import APIRouter, Query

from app.core.stubs import not_implemented
from app.schemas.common import ApiResponse, PageData
from app.schemas.item import ItemAuditRequest, ItemOut
from app.schemas.report import ReportHandleRequest, ReportOut

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/items/pending", response_model=ApiResponse[PageData[ItemOut]])
def pending_items(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    not_implemented("待审核商品列表")


@router.put("/items/{item_id}/audit", response_model=ApiResponse[dict])
def audit_item(item_id: int, payload: ItemAuditRequest):
    not_implemented("商品审核")


@router.put("/users/{user_id}/ban", response_model=ApiResponse[dict])
def ban_user(user_id: int):
    not_implemented("封禁用户")


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
