from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PageData
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["Order"])

STATUS_MESSAGES = {1: "已确认交易", 2: "交易完成", 3: "订单已取消"}


@router.post(
    "", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED
)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_service.create_order(db, current_user, payload.item_id)
    return ApiResponse(
        code=status.HTTP_201_CREATED,
        msg="订单已发起，请等待卖家确认",
        data={"order_id": order.id},
    )


@router.get("/my", response_model=ApiResponse[PageData[OrderOut]])
def my_orders(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total, rows = order_service.list_my_orders(
        db, current_user.id, page, size
    )
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )


@router.put("/{order_id}/status", response_model=ApiResponse[dict])
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_service.update_status(
        db, current_user, order_id, payload.status
    )
    return ApiResponse(
        msg=STATUS_MESSAGES.get(order.status, "状态已更新"),
        data={"order_id": order.id, "status": order.status},
    )
