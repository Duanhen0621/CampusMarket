from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED_HEADERS = {"WWW-Authenticate": "Bearer"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
            headers=_UNAUTHORIZED_HEADERS,
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的登录凭证",
            headers=_UNAUTHORIZED_HEADERS,
        ) from None

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers=_UNAUTHORIZED_HEADERS,
        )
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已被封禁"
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    return current_user
