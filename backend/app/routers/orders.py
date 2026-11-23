from fastapi import APIRouter, Query, status

from app.core.stubs import not_implemented
from app.schemas.common import ApiResponse, PageData
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["Order"])


@router.post("", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate):
    not_implemented("发起交易订单")


@router.get("/my", response_model=ApiResponse[PageData[OrderOut]])
def my_orders(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    not_implemented("我的订单")


@router.put("/{order_id}/status", response_model=ApiResponse[OrderOut])
def update_order_status(order_id: int, payload: OrderStatusUpdate):
    not_implemented("更新订单状态")
