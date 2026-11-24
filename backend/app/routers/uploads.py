import io
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/uploads", tags=["Upload"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIDE = 1600
MAX_PIXELS = 50_000_000


@router.post(
    "/image",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持 JPG / PNG / WebP / GIF 格式",
        )

    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="上传文件为空"
        )
    if len(data) > settings.max_upload_size:
        limit_mb = settings.max_upload_size // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"图片不能超过 {limit_mb}MB",
        )

    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.width * image.height > MAX_PIXELS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="图片分辨率过大",
                )
            image = image.convert("RGB")
            image.thumbnail((MAX_SIDE, MAX_SIDE))
            filename = f"{uuid4().hex}.jpg"
            upload_dir = settings.upload_path
            upload_dir.mkdir(parents=True, exist_ok=True)
            image.save(upload_dir / filename, "JPEG", quality=85, optimize=True)
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="无法识别的图片文件"
        ) from None

    return ApiResponse(
        code=status.HTTP_201_CREATED,
        msg="上传成功",
        data={"url": f"/uploads/{filename}"},
    )
