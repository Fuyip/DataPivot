"""
案件权限管理API路由
实现案件权限的分配、修改、撤销等功能
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_system_db
from backend.models.case import Case, UserCasePermission
from backend.models.user import User
from backend.schemas.case import (
    UserCasePermission as PermissionSchema,
    UserCasePermissionCreate,
    UserCasePermissionUpdate
)
from backend.schemas.common import success_response, error_response
from backend.services.auth_service import get_current_active_user
from backend.services.case_service import check_case_permission
from backend.schemas.user import User as UserSchema

router = APIRouter(prefix="/cases", tags=["案件权限管理"])


@router.get("/{case_id}/permissions", summary="获取案件的所有权限")
def get_case_permissions(
    case_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    获取案件的所有用户权限
    - 需要对该案件有admin权限
    """
    # 查询案件
    case = db.query(Case).filter(Case.id == case_id, Case.is_active == True).first()
    if not case:
        return error_response(404, "案件不存在")

    # 权限检查
    if current_user.role == "super_admin":
        # 超级管理员可以查看所有案件的权限
        pass
    else:
        # admin 和 user 都需要有该案件的管理权限
        if not check_case_permission(db, current_user.id, case_id, "admin"):
            return error_response(403, "权限不足，需要该案件的管理权限")

    # 查询所有权限
    permissions = db.query(UserCasePermission).filter(
        UserCasePermission.case_id == case_id
    ).all()

    # 关联用户信息
    items = []
    for perm in permissions:
        user = db.query(User).filter(User.id == perm.user_id).first()
        granted_by_user = db.query(User).filter(User.id == perm.granted_by).first() if perm.granted_by else None

        items.append({
            "id": perm.id,
            "user_id": perm.user_id,
            "user_name": user.username if user else None,
            "user_full_name": user.full_name if user else None,
            "case_id": perm.case_id,
            "permission_level": perm.permission_level,
            "granted_by": perm.granted_by,
            "granted_by_name": granted_by_user.username if granted_by_user else None,
            "granted_at": perm.granted_at.isoformat() if perm.granted_at else None
        })

    return success_response(data={"items": items, "total": len(items)})


@router.post("/{case_id}/permissions", summary="分配案件权限")
def create_case_permission(
    case_id: int,
    permission_data: UserCasePermissionCreate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    分配案件权限给用户
    - 需要对该案件有admin权限
    """
    # 查询案件
    case = db.query(Case).filter(Case.id == case_id, Case.is_active == True).first()
    if not case:
        return error_response(404, "案件不存在")

    # 从 Schema 中获取字段
    user_id = permission_data.user_id
    permission_level = permission_data.permission_level

    # 权限检查
    if current_user.role == "super_admin":
        # 超级管理员可以给任何用户分配权限
        pass
    elif current_user.role == "admin":
        # 管理员只能给自己创建的用户分配自己管理的案件权限
        if not check_case_permission(db, current_user.id, case_id, "admin"):
            return error_response(403, "权限不足，需要该案件的管理权限")
        # 检查目标用户是否是自己创建的
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            return error_response(404, "目标用户不存在")
        if target_user.created_by != current_user.id:
            return error_response(403, "权限不足，只能给自己创建的用户分配权限")
    else:
        # 普通用户需要有管理权限
        if not check_case_permission(db, current_user.id, case_id, "admin"):
            return error_response(403, "权限不足，需要该案件的管理权限")

    # 检查目标用户是否存在
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        return error_response(404, "目标用户不存在")

    # 检查是否已有权限
    existing_permission = db.query(UserCasePermission).filter(
        UserCasePermission.user_id == user_id,
        UserCasePermission.case_id == case_id
    ).first()

    if existing_permission:
        return error_response(400, "该用户已有该案件的权限，请使用更新接口修改权限级别")

    # 创建权限
    new_permission = UserCasePermission(
        user_id=user_id,
        case_id=case_id,
        permission_level=permission_level,
        granted_by=current_user.id
    )
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)

    return success_response(
        data={
            "id": new_permission.id,
            "user_id": new_permission.user_id,
            "case_id": new_permission.case_id,
            "permission_level": new_permission.permission_level,
            "granted_by": new_permission.granted_by,
            "granted_at": new_permission.granted_at.isoformat() if new_permission.granted_at else None
        },
        message="权限分配成功"
    )


@router.put("/{case_id}/permissions/{permission_id}", summary="修改权限级别")
def update_case_permission(
    case_id: int,
    permission_id: int,
    permission_data: UserCasePermissionUpdate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    修改用户的案件权限级别
    - 需要对该案件有admin权限
    """
    # 查询案件
    case = db.query(Case).filter(Case.id == case_id, Case.is_active == True).first()
    if not case:
        return error_response(404, "案件不存在")

    # 从 Schema 中获取权限级别
    permission_level = permission_data.permission_level

    # 权限检查
    if current_user.role == "super_admin":
        # 超级管理员可以修改所有权限
        pass
    else:
        # admin 和 user 都需要有该案件的管理权限
        if not check_case_permission(db, current_user.id, case_id, "admin"):
            return error_response(403, "权限不足，需要该案件的管理权限")

    # 查询权限记录
    permission = db.query(UserCasePermission).filter(
        UserCasePermission.id == permission_id,
        UserCasePermission.case_id == case_id
    ).first()

    if not permission:
        return error_response(404, "权限记录不存在")

    # 检查是否是创建者的权限（不允许修改创建者的权限）
    if permission.user_id == case.created_by and permission.permission_level == "admin":
        return error_response(400, "不允许修改案件创建者的管理权限")

    # 更新权限级别
    permission.permission_level = permission_level
    db.commit()
    db.refresh(permission)

    return success_response(
        data={
            "id": permission.id,
            "user_id": permission.user_id,
            "case_id": permission.case_id,
            "permission_level": permission.permission_level,
            "granted_at": permission.granted_at.isoformat() if permission.granted_at else None
        },
        message="权限更新成功"
    )


@router.delete("/{case_id}/permissions/{permission_id}", summary="撤销权限")
def delete_case_permission(
    case_id: int,
    permission_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    撤销用户的案件权限
    - 需要对该案件有admin权限
    - 不允许撤销创建者的权限
    """
    # 查询案件
    case = db.query(Case).filter(Case.id == case_id, Case.is_active == True).first()
    if not case:
        return error_response(404, "案件不存在")

    # 权限检查
    if current_user.role == "super_admin":
        # 超级管理员可以撤销所有权限
        pass
    else:
        # admin 和 user 都需要有该案件的管理权限
        if not check_case_permission(db, current_user.id, case_id, "admin"):
            return error_response(403, "权限不足，需要该案件的管理权限")

    # 查询权限记录
    permission = db.query(UserCasePermission).filter(
        UserCasePermission.id == permission_id,
        UserCasePermission.case_id == case_id
    ).first()

    if not permission:
        return error_response(404, "权限记录不存在")

    # 检查是否是创建者的权限（不允许撤销创建者的权限）
    if permission.user_id == case.created_by:
        return error_response(400, "不允许撤销案件创建者的权限")

    # 删除权限
    db.delete(permission)
    db.commit()

    return success_response(message="权限撤销成功")


@router.get("/users/{user_id}/cases", summary="获取用户的案件列表")
def get_user_cases(
    user_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    获取用户有权限的所有案件
    - 管理员可查看任何用户
    - 普通用户只能查看自己
    """
    # 权限检查
    if current_user.role not in ["super_admin", "admin"] and current_user.id != user_id:
        return error_response(403, "权限不足，只能查看自己的案件列表")

    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error_response(404, "用户不存在")

    # 查询用户的所有案件权限
    permissions = db.query(UserCasePermission).filter(
        UserCasePermission.user_id == user_id
    ).all()

    case_ids = [p.case_id for p in permissions]

    # 查询案件信息
    cases = db.query(Case).filter(
        Case.id.in_(case_ids),
        Case.is_active == True
    ).all()

    # 构建返回数据
    items = []
    for case in cases:
        # 获取该用户对该案件的权限级别
        perm = next((p for p in permissions if p.case_id == case.id), None)

        items.append({
            "id": case.id,
            "case_name": case.case_name,
            "case_code": case.case_code,
            "description": case.description,
            "status": case.status,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "permission_level": perm.permission_level if perm else None
        })

    return success_response(data={"items": items, "total": len(items)})
