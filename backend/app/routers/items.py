from fastapi import APIRouter, Query, status

from app.core.stubs import not_implemented
from app.schemas.common import ApiResponse, PageData
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate

router = APIRouter(prefix="/items", tags=["Item"])


@router.get("", response_model=ApiResponse[PageData[ItemOut]])
def list_items(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    keyword: str | None = None,
    type: int | None = Query(None, ge=1, le=3),
):
    not_implemented("商品列表")


@router.post("", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate):
    not_implemented("发布商品")


@router.get("/{item_id}", response_model=ApiResponse[ItemOut])
def get_item(item_id: int):
    not_implemented("商品详情")


@router.put("/{item_id}", response_model=ApiResponse[ItemOut])
def update_item(item_id: int, payload: ItemUpdate):
    not_implemented("编辑商品")


@router.delete("/{item_id}", response_model=ApiResponse[dict])
def off_shelf_item(item_id: int):
    not_implemented("商品下架")
