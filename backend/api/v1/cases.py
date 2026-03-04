"""
案件管理API路由
实现案件的增删改查、归档等功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from database import get_system_db
from backend.models.case import Case, UserCasePermission
from backend.schemas.case import (
    CaseCreate, CaseUpdate, Case as CaseSchema,
    CaseWithPermissions
)
from backend.schemas.common import success_response, error_response
from backend.services.auth_service import get_current_active_user
from backend.services.case_service import (
    create_case_database, drop_case_database,
    check_case_permission, get_user_cases,
    get_case_permission_level, generate_case_code
)
from backend.schemas.user import User as UserSchema

router = APIRouter(prefix="/cases", tags=["案件管理"])


@router.get("", summary="获取案件列表")
def get_cases(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态筛选"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    获取案件列表
    - 管理员：返回所有案件
    - 普通用户：返回有权限的案件
    """
    # 构建查询（排除已删除的案件）
    query = db.query(Case).filter(Case.is_active == True, Case.is_deleted == False)

    # 根据用户角色过滤案件
    if current_user.role == "super_admin":
        # 超级管理员可以查看所有案件
        pass
    elif current_user.role == "admin":
        # 管理员只能查看自己是管理员的案件
        admin_permissions = db.query(UserCasePermission).filter(
            UserCasePermission.user_id == current_user.id,
            UserCasePermission.permission_level == "admin"
        ).all()
        case_ids = [p.case_id for p in admin_permissions]
        if not case_ids:
            return success_response(data={"items": [], "total": 0, "page": page, "page_size": page_size})
        query = query.filter(Case.id.in_(case_ids))
    else:
        # 普通用户只返回有权限的案件
        user_cases = get_user_cases(db, current_user.id)
        case_ids = [c.id for c in user_cases]
        if not case_ids:
            return success_response(data={"items": [], "total": 0, "page": page, "page_size": page_size})
        query = query.filter(Case.id.in_(case_ids))

    # 搜索过滤
    if search:
        query = query.filter(
            or_(
                Case.case_name.like(f"%{search}%"),
                Case.case_code.like(f"%{search}%"),
                Case.description.like(f"%{search}%")
            )
        )

    # 状态过滤
    if status:
        query = query.filter(Case.status == status)

    # 总数
    total = query.count()

    # 分页
    cases = query.order_by(Case.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 添加用户权限信息
    items = []
    for case in cases:
        case_dict = {
            "id": case.id,
            "case_name": case.case_name,
            "case_code": case.case_code,
            "database_name": case.database_name,
            "description": case.description,
            "status": case.status,
            "is_active": case.is_active,
            "created_by": case.created_by,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        }

        # 添加当前用户的权限级别
        if current_user.role == "super_admin":
            case_dict["user_permission"] = "admin"
        else:
            case_dict["user_permission"] = get_case_permission_level(db, current_user.id, case.id)

        items.append(case_dict)

    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/{case_id}", summary="获取案件详情")
def get_case(
    case_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """获取案件详情"""
    # 查询案件（排除已删除的案件）
    case = db.query(Case).filter(Case.id == case_id, Case.is_active == True, Case.is_deleted == False).first()
    if not case:
        return error_response(404, "案件不存在")

    # 权限检查
    if current_user.role == "super_admin":
        # 超级管理员可以访问所有案件
        pass
    else:
        # admin 和 user 都需要检查案件权限
        if not check_case_permission(db, current_user.id, case_id, "read"):
            return error_response(403, "权限不足，无法访问该案件")

    # 获取用户权限级别
    if current_user.role == "super_admin":
        user_permission = "admin"
    else:
        user_permission = get_case_permission_level(db, current_user.id, case_id)

    return success_response(
        data={
            "id": case.id,
            "case_name": case.case_name,
            "case_code": case.case_code,
            "database_name": case.database_name,
            "description": case.description,
            "status": case.status,
            "is_active": case.is_active,
            "created_by": case.created_by,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
            "user_permission": user_permission
        }
    )


@router.post("", summary="创建案件")
def create_case(
    case_data: CaseCreate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    创建案件
    - 仅管理员可创建
    - 自动创建案件数据库
    - 自动给创建者分配admin权限
    """
    # 权限检查
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，需要管理员权限")

    # 如果没有提供案件编号，自动生成
    if not case_data.case_code:
        case_data.case_code = generate_case_code(db)

    # 检查案件名称是否已存在
    existing_case = db.query(Case).filter(Case.case_name == case_data.case_name).first()
    if existing_case:
        return error_response(400, "案件名称已存在")

    # 检查案件编号是否已存在
    existing_code = db.query(Case).filter(Case.case_code == case_data.case_code).first()
    if existing_code:
        return error_response(400, "案件编号已存在")

    # 创建案件记录（先不设置database_name）
    new_case = Case(
        case_name=case_data.case_name,
        case_code=case_data.case_code,
        database_name="",  # 临时值
        description=case_data.description,
        created_by=current_user.id
    )
    db.add(new_case)
    db.flush()  # 获取案件ID

    try:
        # 创建案件数据库
        database_name = create_case_database(new_case.id, new_case.case_name, new_case.case_code)
        new_case.database_name = database_name

        # 给创建者分配admin权限
        permission = UserCasePermission(
            user_id=current_user.id,
            case_id=new_case.id,
            permission_level="admin",
            granted_by=current_user.id
        )
        db.add(permission)

        db.commit()
        db.refresh(new_case)

        return success_response(
            data={
                "id": new_case.id,
                "case_name": new_case.case_name,
                "case_code": new_case.case_code,
                "database_name": new_case.database_name,
                "description": new_case.description,
                "status": new_case.status,
                "created_by": new_case.created_by,
                "created_at": new_case.created_at.isoformat() if new_case.created_at else None
            },
            message="案件创建成功"
        )
    except Exception as e:
        db.rollback()
        # 如果创建失败，尝试删除已创建的数据库
        if new_case.database_name:
            try:
                drop_case_database(new_case.database_name)
            except:
                pass
        return error_response(500, f"案件创建失败: {str(e)}")


@router.put("/{case_id}", summary="更新案件信息")
def update_case(
    case_id: int,
    case_data: CaseUpdate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    更新案件信息
    - 需要对该案件有admin权限
    """
    # 查询案件（排除已删除的案件）
    case = db.query(Case).filter(Case.id == case_id, Case.is_active == True, Case.is_deleted == False).first()
    if not case:
        return error_response(404, "案件不存在")

    # 权限检查
    if current_user.role == "super_admin":
        # 超级管理员可以更新所有案件
        pass
    else:
        # admin 和 user 都需要有该案件的管理权限
        if not check_case_permission(db, current_user.id, case_id, "admin"):
            return error_response(403, "权限不足，需要该案件的管理权限")

    # 更新字段
    if case_data.case_name is not None:
        # 检查名称是否重复
        existing = db.query(Case).filter(
            Case.case_name == case_data.case_name,
            Case.id != case_id
        ).first()
        if existing:
            return error_response(400, "案件名称已存在")
        case.case_name = case_data.case_name

    if case_data.description is not None:
        case.description = case_data.description

    if case_data.status is not None:
        case.status = case_data.status

    if case_data.is_active is not None:
        case.is_active = case_data.is_active

    db.commit()
    db.refresh(case)

    return success_response(
        data={
            "id": case.id,
            "case_name": case.case_name,
            "case_code": case.case_code,
            "database_name": case.database_name,
            "description": case.description,
            "status": case.status,
            "is_active": case.is_active,
            "updated_at": case.updated_at.isoformat() if case.updated_at else None
        },
        message="案件更新成功"
    )


@router.delete("/{case_id}", summary="删除案件（软删除）")
def delete_case(
    case_id: int,
    confirm: bool = Query(False, description="是否确认删除"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    删除案件（软删除）
    - super_admin 可以删除任何案件
    - admin 只能软删除自己创建的案件
    - 需要确认参数 confirm=true
    - 软删除后可以恢复
    - 不会删除案件数据库
    """
    # 权限检查
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，需要管理员权限")

    # 确认检查
    if not confirm:
        return error_response(400, "删除操作需要确认，请设置 confirm=true")

    # 查询案件（包括已删除的，避免重复删除）
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return error_response(404, "案件不存在")

    # 检查是否已删除
    if case.is_deleted:
        return error_response(400, "案件已被删除")

    # admin 只能删除自己创建的案件
    if current_user.role == "admin":
        if case.created_by != current_user.id:
            return error_response(403, "权限不足，只能删除自己创建的案件")

    try:
        # 软删除：标记为已删除
        case.is_deleted = True
        case.deleted_at = func.now()
        case.deleted_by = current_user.id

        db.commit()
        db.refresh(case)

        return success_response(
            message="案件已删除（软删除），可通过恢复功能恢复",
            data={
                "id": case.id,
                "case_name": case.case_name,
                "deleted_at": case.deleted_at.isoformat() if case.deleted_at else None
            }
        )
    except Exception as e:
        db.rollback()
        return error_response(500, f"案件删除失败: {str(e)}")


@router.post("/{case_id}/archive", summary="归档案件")
def archive_case(
    case_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    归档案件
    - 需要对该案件有admin权限
    """
    # 查询案件（排除已删除的案件）
    case = db.query(Case).filter(Case.id == case_id, Case.is_active == True, Case.is_deleted == False).first()
    if not case:
        return error_response(404, "案件不存在")

    # 权限检查
    if current_user.role == "super_admin":
        # 超级管理员可以归档所有案件
        pass
    else:
        # admin 和 user 都需要有该案件的管理权限
        if not check_case_permission(db, current_user.id, case_id, "admin"):
            return error_response(403, "权限不足，需要该案件的管理权限")

    # 归档
    case.status = "archived"
    db.commit()

    return success_response(message="案件归档成功")


@router.get("/deleted/list", summary="获取已删除案件列表")
def get_deleted_cases(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    获取已删除案件列表
    - 仅管理员可查看
    """
    # 权限检查
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，需要管理员权限")

    # 构建查询（只查询已删除的案件）
    query = db.query(Case).filter(Case.is_deleted == True)

    # 搜索过滤
    if search:
        query = query.filter(
            or_(
                Case.case_name.like(f"%{search}%"),
                Case.case_code.like(f"%{search}%"),
                Case.description.like(f"%{search}%")
            )
        )

    # 总数
    total = query.count()

    # 分页
    cases = query.order_by(Case.deleted_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 构建返回数据
    items = []
    for case in cases:
        items.append({
            "id": case.id,
            "case_name": case.case_name,
            "case_code": case.case_code,
            "database_name": case.database_name,
            "description": case.description,
            "status": case.status,
            "created_by": case.created_by,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "deleted_at": case.deleted_at.isoformat() if case.deleted_at else None,
            "deleted_by": case.deleted_by
        })

    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.post("/{case_id}/restore", summary="恢复已删除案件")
def restore_case(
    case_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    恢复已删除案件
    - super_admin 可以恢复任何案件
    - admin 只能恢复自己删除的案件
    """
    # 权限检查
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，需要管理员权限")

    # 查询案件
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return error_response(404, "案件不存在")

    # 检查是否已删除
    if not case.is_deleted:
        return error_response(400, "案件未被删除，无需恢复")

    # admin 只能恢复自己删除的案件
    if current_user.role == "admin":
        if case.deleted_by != current_user.id:
            return error_response(403, "权限不足，只能恢复自己删除的案件")

    try:
        # 恢复：清除删除标记
        case.is_deleted = False
        case.deleted_at = None
        case.deleted_by = None

        db.commit()
        db.refresh(case)

        return success_response(
            message="案件恢复成功",
            data={
                "id": case.id,
                "case_name": case.case_name,
                "case_code": case.case_code,
                "status": case.status
            }
        )
    except Exception as e:
        db.rollback()
        return error_response(500, f"案件恢复失败: {str(e)}")


@router.delete("/{case_id}/permanent", summary="永久删除案件")
def permanent_delete_case(
    case_id: int,
    confirm: bool = Query(False, description="是否确认永久删除"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    永久删除案件（硬删除）
    - 仅 super_admin 可操作
    - 需要确认参数 confirm=true
    - 删除案件记录和相关权限
    - 删除案件数据库
    - 此操作不可恢复
    """
    # 权限检查 - 只有 super_admin 可以永久删除
    if current_user.role != "super_admin":
        return error_response(403, "权限不足，需要超级管理员权限")

    # 确认检查
    if not confirm:
        return error_response(400, "永久删除操作需要确认，请设置 confirm=true")

    # 查询案件
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return error_response(404, "案件不存在")

    # 建议只能永久删除已软删除的案件
    if not case.is_deleted:
        return error_response(400, "请先执行软删除操作，再进行永久删除")

    # 保存数据库名称用于删除
    database_name = case.database_name

    try:
        # 删除案件相关的所有权限记录
        deleted_permissions = db.query(UserCasePermission).filter(
            UserCasePermission.case_id == case_id
        ).delete(synchronize_session=False)

        # 删除案件记录
        db.delete(case)
        db.commit()

        # 删除案件数据库
        if database_name:
            try:
                drop_case_database(database_name)
            except Exception as e:
                # 数据库删除失败不影响案件记录删除
                print(f"删除案件数据库失败: {str(e)}")

        return success_response(message=f"案件永久删除成功，已删除 {deleted_permissions} 条权限记录")
    except Exception as e:
        db.rollback()
        return error_response(500, f"案件永久删除失败: {str(e)}")
