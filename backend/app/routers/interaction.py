from fastapi import APIRouter, Query, status

from app.core.stubs import not_implemented
from app.schemas.common import ApiResponse, PageData
from app.schemas.interaction import FavoriteOut, MessageCreate, MessageOut

router = APIRouter(prefix="/items", tags=["Interaction"])


@router.get("/{item_id}/messages", response_model=ApiResponse[PageData[MessageOut]])
def list_messages(
    item_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    not_implemented("留言列表")


@router.post(
    "/{item_id}/messages",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
)
def create_message(item_id: int, payload: MessageCreate):
    not_implemented("发表留言")


@router.post(
    "/{item_id}/favorite",
    response_model=ApiResponse[FavoriteOut],
    status_code=status.HTTP_201_CREATED,
)
def add_favorite(item_id: int):
    not_implemented("收藏商品")


@router.delete("/{item_id}/favorite", response_model=ApiResponse[dict])
def remove_favorite(item_id: int):
    not_implemented("取消收藏")
