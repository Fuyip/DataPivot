"""
权限管理 API 路由
实现权限的管理和分配功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_system_db
from backend.models.user import User
from backend.models.permission import Permission, PREDEFINED_PERMISSIONS
from backend.models.case import UserCasePermission
from backend.schemas.permission import (
    PermissionCreate, Permission as PermissionSchema,
    UserCasePermissionCreate, UserCasePermissionUpdate,
    UserCasePermission as UserCasePermissionSchema
)
from backend.schemas.common import success_response, error_response
from backend.services.auth_service import get_current_active_user

router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.get("", summary="获取权限列表")
def get_permissions(
    category: Optional[str] = Query(None, description="权限分类筛选"),
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有权限列表

    Args:
        category: 权限分类筛选
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 权限列表
    """
    # 构建查询
    query = db.query(Permission).filter(Permission.is_active == True)

    if category:
        query = query.filter(Permission.category == category)

    permissions = query.all()

    return success_response(
        data={
            "items": [
                {
                    "id": p.id,
                    "code": p.code,
                    "name": p.name,
                    "description": p.description,
                    "category": p.category
                }
                for p in permissions
            ],
            "total": len(permissions)
        }
    )


@router.post("/init", summary="初始化预定义权限")
def init_permissions(
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    初始化预定义权限（仅超级管理员可用）

    Args:
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 初始化结果
    """
    # 检查权限
    if current_user.role != "super_admin":
        return error_response(403, "权限不足，需要超级管理员权限")

    created_count = 0
    for perm_data in PREDEFINED_PERMISSIONS:
        # 检查权限是否已存在
        existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            created_count += 1

    db.commit()

    return success_response(
        message=f"成功初始化 {created_count} 个权限"
    )


@router.post("/case-permissions", summary="分配案件权限")
def create_case_permission(
    permission_data: UserCasePermissionCreate,
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    为用户分配案件权限

    超级管理员：可以为任何案件分配权限
    管理员：可以为自己有管理权限的案件分配权限

    Args:
        permission_data: 权限分配数据
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 分配结果
    """
    # 检查权限
    if current_user.role == "super_admin":
        # 超级管理员可以分配任何案件的权限
        pass
    elif current_user.role == "admin":
        # 管理员需要检查是否对该案件有管理权限
        existing_perm = db.query(UserCasePermission).filter(
            UserCasePermission.user_id == current_user.id,
            UserCasePermission.case_id == permission_data.case_id,
            UserCasePermission.role == "admin"
        ).first()
        if not existing_perm:
            return error_response(403, "您没有该案件的管理权限")
    else:
        return error_response(403, "权限不足")

    # 检查用户是否存在
    target_user = db.query(User).filter(User.id == permission_data.user_id).first()
    if not target_user:
        return error_response(404, "目标用户不存在")

    # 检查是否已有权限记录
    existing = db.query(UserCasePermission).filter(
        UserCasePermission.user_id == permission_data.user_id,
        UserCasePermission.case_id == permission_data.case_id
    ).first()

    if existing:
        return error_response(400, "该用户已有此案件的权限，请使用更新接口")

    # 创建权限记录
    case_permission = UserCasePermission(
        user_id=permission_data.user_id,
        case_id=permission_data.case_id,
        role=permission_data.role,
        granted_by=current_user.id
    )

    # 添加具体权限
    if permission_data.permission_codes:
        permissions = db.query(Permission).filter(
            Permission.code.in_(permission_data.permission_codes)
        ).all()
        case_permission.permissions = permissions

    db.add(case_permission)
    db.commit()
    db.refresh(case_permission)

    return success_response(
        data={
            "id": case_permission.id,
            "user_id": case_permission.user_id,
            "case_id": case_permission.case_id,
            "role": case_permission.role,
            "permissions": [p.code for p in case_permission.permissions]
        },
        message="案件权限分配成功"
    )


@router.put("/case-permissions/{permission_id}", summary="更新案件权限")
def update_case_permission(
    permission_id: int,
    permission_data: UserCasePermissionUpdate,
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新用户的案件权限

    Args:
        permission_id: 权限记录ID
        permission_data: 更新数据
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 更新结果
    """
    # 查找权限记录
    case_permission = db.query(UserCasePermission).filter(
        UserCasePermission.id == permission_id
    ).first()

    if not case_permission:
        return error_response(404, "权限记录不存在")

    # 检查权限
    if current_user.role == "super_admin":
        pass
    elif current_user.role == "admin":
        # 检查是否对该案件有管理权限
        admin_perm = db.query(UserCasePermission).filter(
            UserCasePermission.user_id == current_user.id,
            UserCasePermission.case_id == case_permission.case_id,
            UserCasePermission.role == "admin"
        ).first()
        if not admin_perm:
            return error_response(403, "您没有该案件的管理权限")
    else:
        return error_response(403, "权限不足")

    # 更新角色
    if permission_data.role is not None:
        case_permission.role = permission_data.role

    # 更新权限列表
    if permission_data.permission_codes is not None:
        permissions = db.query(Permission).filter(
            Permission.code.in_(permission_data.permission_codes)
        ).all()
        case_permission.permissions = permissions

    db.commit()
    db.refresh(case_permission)

    return success_response(
        data={
            "id": case_permission.id,
            "user_id": case_permission.user_id,
            "case_id": case_permission.case_id,
            "role": case_permission.role,
            "permissions": [p.code for p in case_permission.permissions]
        },
        message="案件权限更新成功"
    )


@router.delete("/case-permissions/{permission_id}", summary="删除案件权限")
def delete_case_permission(
    permission_id: int,
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除用户的案件权限

    Args:
        permission_id: 权限记录ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 删除结果
    """
    # 查找权限记录
    case_permission = db.query(UserCasePermission).filter(
        UserCasePermission.id == permission_id
    ).first()

    if not case_permission:
        return error_response(404, "权限记录不存在")

    # 检查权限
    if current_user.role == "super_admin":
        pass
    elif current_user.role == "admin":
        # 检查是否对该案件有管理权限
        admin_perm = db.query(UserCasePermission).filter(
            UserCasePermission.user_id == current_user.id,
            UserCasePermission.case_id == case_permission.case_id,
            UserCasePermission.role == "admin"
        ).first()
        if not admin_perm:
            return error_response(403, "您没有该案件的管理权限")
    else:
        return error_response(403, "权限不足")

    db.delete(case_permission)
    db.commit()

    return success_response(message="案件权限删除成功")


@router.get("/case-permissions/case/{case_id}", summary="获取案件的所有权限分配")
def get_case_permissions(
    case_id: int,
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定案件的所有权限分配

    Args:
        case_id: 案件ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 权限分配列表
    """
    # 检查权限
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足")

    permissions = db.query(UserCasePermission).filter(
        UserCasePermission.case_id == case_id
    ).all()

    return success_response(
        data={
            "items": [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "case_id": p.case_id,
                    "role": p.role,
                    "permissions": [perm.code for perm in p.permissions],
                    "granted_by": p.granted_by,
                    "granted_at": p.granted_at.isoformat() if p.granted_at else None
                }
                for p in permissions
            ],
            "total": len(permissions)
        }
    )


@router.get("/case-permissions/user/{user_id}", summary="获取用户的所有案件权限")
def get_user_case_permissions(
    user_id: int,
    db: Session = Depends(get_system_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定用户的所有案件权限

    Args:
        user_id: 用户ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 权限列表
    """
    # 只能查看自己的权限，或者管理员可以查看所有人的
    if current_user.role not in ["super_admin", "admin"] and current_user.id != user_id:
        return error_response(403, "权限不足")

    permissions = db.query(UserCasePermission).filter(
        UserCasePermission.user_id == user_id
    ).all()

    return success_response(
        data={
            "items": [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "case_id": p.case_id,
                    "role": p.role,
                    "permissions": [perm.code for perm in p.permissions],
                    "granted_by": p.granted_by,
                    "granted_at": p.granted_at.isoformat() if p.granted_at else None
                }
                for p in permissions
            ],
            "total": len(permissions)
        }
    )
