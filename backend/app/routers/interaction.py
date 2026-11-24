from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PageData
from app.schemas.interaction import MessageCreate, MessageOut
from app.schemas.item import ItemOut
from app.services import interaction_service

router = APIRouter(prefix="/items", tags=["Interaction"])
favorites_router = APIRouter(prefix="/favorites", tags=["Interaction"])


@router.get("/{item_id}/messages", response_model=ApiResponse[PageData[MessageOut]])
def list_messages(
    item_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total, rows = interaction_service.list_messages(db, item_id, page, size)
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )


@router.post(
    "/{item_id}/messages",
    response_model=ApiResponse[MessageOut],
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    item_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = interaction_service.create_message(
        db, current_user, item_id, payload.content
    )
    return ApiResponse(
        code=status.HTTP_201_CREATED, msg="留言成功", data=message
    )


@router.post(
    "/{item_id}/favorite",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
)
def add_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    favorite = interaction_service.add_favorite(db, current_user, item_id)
    return ApiResponse(
        code=status.HTTP_201_CREATED,
        msg="收藏成功",
        data={"favorite_id": favorite.id},
    )


@router.delete("/{item_id}/favorite", response_model=ApiResponse[dict])
def remove_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interaction_service.remove_favorite(db, current_user, item_id)
    return ApiResponse(msg="已取消收藏")


@favorites_router.get("/my", response_model=ApiResponse[PageData[ItemOut]])
def my_favorites(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total, rows = interaction_service.list_favorites(
        db, current_user.id, page, size
    )
    return ApiResponse(
        data=PageData(total=total, page=page, size=size, list=rows)
    )


@favorites_router.get("/check/{item_id}", response_model=ApiResponse[dict])
def check_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(
        data={
            "favorited": interaction_service.is_favorited(
                db, current_user.id, item_id
            )
        }
    )
