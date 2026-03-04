"""
认证相关API路由
实现登录、登出、Token刷新等接口
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_system_db
from backend.schemas.auth import LoginRequest, Token
from backend.schemas.user import User as UserSchema
from backend.schemas.common import success_response, error_response
from backend.services.auth_service import authenticate_user, get_current_active_user
from backend.core.security import create_access_token
from backend.core.config import config

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", summary="用户登录")
def login(login_data: LoginRequest, db: Session = Depends(get_system_db)):
    """
    用户登录接口

    Args:
        login_data: 登录请求数据（用户名和密码）
        db: 数据库会话

    Returns:
        dict: 包含访问令牌和用户信息的响应
    """
    # 验证用户名和密码
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        return error_response(401, "用户名或密码错误")

    # 检查用户是否激活
    if not user.is_active:
        return error_response(403, "用户已被禁用")

    # 创建访问令牌
    access_token_expires = timedelta(minutes=config.JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )

    # 返回响应
    return success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": config.JWT_EXPIRE_MINUTES * 60,  # 转换为秒
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "full_name": user.full_name,
                "email": user.email
            }
        },
        message="登录成功"
    )


@router.post("/logout", summary="用户登出")
def logout(current_user: UserSchema = Depends(get_current_active_user)):
    """
    用户登出接口

    Args:
        current_user: 当前登录用户

    Returns:
        dict: 登出成功响应
    """
    # 注意：JWT是无状态的，真正的登出需要实现Token黑名单
    # 这里只是返回成功响应，客户端需要删除本地存储的Token
    return success_response(message="退出成功")


@router.post("/refresh", summary="刷新Token")
def refresh_token(current_user: UserSchema = Depends(get_current_active_user)):
    """
    刷新访问令牌

    Args:
        current_user: 当前登录用户

    Returns:
        dict: 包含新访问令牌的响应
    """
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=config.JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username, "user_id": current_user.id},
        expires_delta=access_token_expires
    )

    return success_response(
        data={
            "access_token": access_token,
            "expires_in": config.JWT_EXPIRE_MINUTES * 60
        }
    )


@router.get("/me", summary="获取当前用户信息")
def get_current_user_info(current_user: UserSchema = Depends(get_current_active_user)):
    """
    获取当前登录用户的信息

    Args:
        current_user: 当前登录用户

    Returns:
        dict: 用户信息
    """
    return success_response(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        }
    )
