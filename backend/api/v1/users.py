"""
用户管理 API 路由
实现用户的增删改查功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_system_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserUpdate, User as UserSchema
from backend.schemas.common import success_response, error_response
from backend.services.auth_service import get_current_active_user
from backend.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", summary="获取用户列表")
def get_users(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    username: Optional[str] = Query(None, description="用户名搜索"),
    role: Optional[str] = Query(None, description="角色筛选"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取用户列表（需要管理员权限）

    Args:
        skip: 跳过的记录数（分页）
        limit: 返回的记录数（分页）
        username: 用户名模糊搜索
        role: 角色筛选
        is_active: 激活状态筛选
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 用户列表和总数
    """
    # 检查权限
    if current_user.role != "admin":
        return error_response(403, "权限不足，需要管理员权限")

    # 构建查询
    query = db.query(User)

    # 应用筛选条件
    if username:
        query = query.filter(User.username.like(f"%{username}%"))
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # 获取总数
    total = query.count()

    # 分页查询
    users = query.offset(skip).limit(limit).all()

    # 转换为响应格式
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        for user in users
    ]

    return success_response(
        data={
            "items": users_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{user_id}", summary="获取用户详情")
def get_user(
    user_id: int,
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定用户的详细信息

    Args:
        user_id: 用户ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 用户详细信息
    """
    # 只有管理员或用户本人可以查看
    if current_user.role != "admin" and current_user.id != user_id:
        return error_response(403, "权限不足")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error_response(404, "用户不存在")

    return success_response(
        data={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    )


@router.post("", summary="创建用户")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新用户（需要管理员权限）

    Args:
        user_data: 用户创建数据
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 创建的用户信息
    """
    # 检查权限
    if current_user.role != "admin":
        return error_response(403, "权限不足，需要管理员权限")

    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return error_response(400, "用户名已存在")

    # 检查邮箱是否已存在
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            return error_response(400, "邮箱已被使用")

    # 创建新用户
    new_user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        email=user_data.email,
        role="user",  # 默认角色为普通用户
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return success_response(
        data={
            "id": new_user.id,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "email": new_user.email,
            "role": new_user.role,
            "is_active": new_user.is_active
        },
        message="用户创建成功"
    )


@router.put("/{user_id}", summary="更新用户信息")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新用户信息

    Args:
        user_id: 用户ID
        user_data: 用户更新数据
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 更新后的用户信息
    """
    # 只有管理员或用户本人可以更新
    if current_user.role != "admin" and current_user.id != user_id:
        return error_response(403, "权限不足")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error_response(404, "用户不存在")

    # 更新字段
    if user_data.email is not None:
        # 检查邮箱是否被其他用户使用
        existing_email = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing_email:
            return error_response(400, "邮箱已被使用")
        user.email = user_data.email

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)

    # 只有管理员可以修改激活状态
    if user_data.is_active is not None:
        if current_user.role != "admin":
            return error_response(403, "只有管理员可以修改用户激活状态")
        user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)

    return success_response(
        data={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        },
        message="用户信息更新成功"
    )


@router.delete("/{user_id}", summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除用户（需要管理员权限）

    Args:
        user_id: 用户ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 删除结果
    """
    # 检查权限
    if current_user.role != "admin":
        return error_response(403, "权限不足，需要管理员权限")

    # 不能删除自己
    if current_user.id == user_id:
        return error_response(400, "不能删除自己的账户")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error_response(404, "用户不存在")

    db.delete(user)
    db.commit()

    return success_response(message="用户删除成功")


@router.put("/{user_id}/role", summary="修改用户角色")
def update_user_role(
    user_id: int,
    role: str = Query(..., regex="^(admin|user)$", description="角色: admin 或 user"),
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    修改用户角色（需要管理员权限）

    Args:
        user_id: 用户ID
        role: 新角色
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 更新结果
    """
    # 检查权限
    if current_user.role != "admin":
        return error_response(403, "权限不足，需要管理员权限")

    # 不能修改自己的角色
    if current_user.id == user_id:
        return error_response(400, "不能修改自己的角色")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error_response(404, "用户不存在")

    user.role = role
    db.commit()
    db.refresh(user)

    return success_response(
        data={
            "id": user.id,
            "username": user.username,
            "role": user.role
        },
        message=f"用户角色已更新为 {role}"
    )


@router.put("/{user_id}/password", summary="重置用户密码")
def reset_user_password(
    user_id: int,
    new_password: str = Query(..., min_length=6, description="新密码"),
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    重置用户密码（管理员可以重置任何用户，用户只能重置自己）

    Args:
        user_id: 用户ID
        new_password: 新密码
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 重置结果
    """
    # 只有管理员或用户本人可以重置密码
    if current_user.role != "admin" and current_user.id != user_id:
        return error_response(403, "权限不足")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error_response(404, "用户不存在")

    user.hashed_password = get_password_hash(new_password)
    db.commit()

    return success_response(message="密码重置成功")
