from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PageData
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate
from app.services import item_service

router = APIRouter(prefix="/items", tags=["Item"])


@router.get("", response_model=ApiResponse[PageData[ItemOut]])
def list_items(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=50),
    keyword: str | None = None,
    type: int | None = Query(None, ge=1, le=3),
    db: Session = Depends(get_db),
):
    total, rows = item_service.list_public_items(db, page, size, keyword, type)
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )


@router.get("/my", response_model=ApiResponse[PageData[ItemOut]])
def my_items(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=50),
    status: int | None = Query(None, ge=0, le=3),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total, rows = item_service.list_user_items(
        db, current_user.id, page, size, status
    )
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )


@router.post(
    "", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED
)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = item_service.create_item(db, current_user, payload)
    return ApiResponse(
        code=status.HTTP_201_CREATED,
        msg="发布成功，等待审核",
        data={"item_id": item.id},
    )


@router.get("/{item_id}", response_model=ApiResponse[ItemOut])
def get_item(item_id: int, db: Session = Depends(get_db)):
    return ApiResponse(data=item_service.get_public_item(db, item_id))


@router.get("/{item_id}/edit", response_model=ApiResponse[ItemOut])
def get_item_for_edit(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = item_service.get_owned_item(db, item_id, current_user)
    return ApiResponse(data=item_service.to_item_out(item))


@router.put("/{item_id}", response_model=ApiResponse[ItemOut])
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = item_service.get_owned_item(db, item_id, current_user)
    item = item_service.update_item(db, item, payload)
    return ApiResponse(
        msg="修改成功，重新进入审核", data=item_service.to_item_out(item)
    )


@router.delete("/{item_id}", response_model=ApiResponse[dict])
def off_shelf_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = item_service.get_owned_item(db, item_id, current_user)
    item_service.off_shelf_item(db, item)
    return ApiResponse(msg="商品已下架")
