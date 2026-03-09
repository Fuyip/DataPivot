"""
认证服务层
实现用户认证的业务逻辑
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_system_db
from backend.models.user import User
from backend.core.security import verify_password, decode_access_token
from backend.schemas.auth import TokenData

# HTTP Bearer Token 认证方案
security = HTTPBearer()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    验证用户名和密码

    Args:
        db: 数据库会话
        username: 用户名
        password: 密码

    Returns:
        Optional[User]: 验证成功返回用户对象，失败返回 None
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_system_db)
) -> User:
    """
    从 Token 获取当前用户

    Args:
        credentials: HTTP 认证凭证
        db: 数据库会话

    Returns:
        User: 当前用户对象

    Raises:
        HTTPException: 认证失败时抛出 401 异常
    """
    token = credentials.credentials

    # 解码 Token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从 payload 中获取用户名
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查询用户
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前激活用户（用于依赖注入）

    Args:
        current_user: 当前用户

    Returns:
        User: 当前激活用户

    Raises:
        HTTPException: 用户未激活时抛出 400 异常
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    要求管理员或超级管理员权限

    Args:
        current_user: 当前用户

    Returns:
        User: 当前用户

    Raises:
        HTTPException: 权限不足时抛出 403 异常
    """
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


def require_super_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    要求超级管理员权限

    Args:
        current_user: 当前用户

    Returns:
        User: 当前用户

    Raises:
        HTTPException: 权限不足时抛出 403 异常
    """
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级管理员权限"
        )
    return current_user
