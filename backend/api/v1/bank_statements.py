"""
银行流水API路由
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import uuid

from database import get_system_db
from backend.models.case import Case
from backend.models.bank_statement_task import BankStatementTask
from backend.schemas.bank_statement import (
    BankStatementUploadResponse, TaskProgress, TaskStatistics, TaskListItem
)
from backend.schemas.common import success_response, error_response
from backend.services.auth_service import get_current_active_user
from backend.services.case_service import check_case_permission
from backend.services.file_storage_service import FileStorageService
from backend.tasks.bank_statement_tasks import process_bank_statements
from backend.schemas.user import User as UserSchema

router = APIRouter(tags=["银行流水"])


@router.post("/cases/{case_id}/bank-statements/upload", summary="上传银行流水文件")
async def upload_bank_statements(
    case_id: int,
    files: List[UploadFile] = File(..., description="银行流水压缩包"),
    relative_paths_json: Optional[str] = Form(None, description="目录上传时的相对路径JSON数组"),
    template_id: Optional[int] = Form(None, description="导入规则模板ID"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    上传银行流水文件
    - 需要对案件有write权限
    - 支持上传多个压缩包
    - 返回任务ID用于查询进度
    """
    # 权限检查
    if current_user.role != "super_admin":
        if not check_case_permission(db, current_user.id, case_id, "write"):
            return error_response(403, "权限不足，需要写入权限")

    # 查询案件
    case = db.query(Case).filter(
        Case.id == case_id,
        Case.is_active == True,
        Case.is_deleted == False
    ).first()

    if not case:
        return error_response(404, "案件不存在")

    # 生成任务ID
    task_id = str(uuid.uuid4())

    # 保存文件
    file_service = FileStorageService()
    upload_dir = file_service.get_case_upload_dir(case_id, task_id)

    file_names = []
    total_size = 0
    relative_paths: List[Optional[str]] = []

    if relative_paths_json:
        try:
            parsed_relative_paths = json.loads(relative_paths_json)
            if not isinstance(parsed_relative_paths, list):
                return error_response(400, "relative_paths_json 必须是数组")
            relative_paths = parsed_relative_paths
        except json.JSONDecodeError:
            return error_response(400, "relative_paths_json 不是合法的 JSON")

    for index, file in enumerate(files):
        relative_path = None
        if relative_paths and index < len(relative_paths):
            relative_path = relative_paths[index]

        filename, file_size = await file_service.save_upload_file(
            file,
            upload_dir,
            relative_path
        )
        file_names.append(filename)
        total_size += file_size

    # 创建任务记录
    task = BankStatementTask(
        case_id=case_id,
        task_id=task_id,
        template_id=template_id,
        status="pending",
        file_count=len(files),
        file_names=file_names,
        file_size_total=total_size,
        created_by=current_user.id,
        storage_path=str(upload_dir)
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # 启动异步任务
    process_bank_statements.delay(
        case_id=case_id,
        database_name=case.database_name,
        task_id=task_id,
        storage_path=str(upload_dir),
        template_id=template_id
    )

    return success_response(
        data={
            "task_id": task_id,
            "message": "文件上传成功，开始处理",
            "file_count": len(files),
            "estimated_time": None
        },
        message="银行流水文件上传成功"
    )


@router.get("/cases/{case_id}/bank-statements/tasks/{task_id}", summary="查询任务进度")
def get_task_progress(
    case_id: int,
    task_id: str,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    查询任务进度
    - 需要对案件有read权限
    """
    # 权限检查
    if current_user.role != "super_admin":
        if not check_case_permission(db, current_user.id, case_id, "read"):
            return error_response(403, "权限不足")

    # 查询任务
    task = db.query(BankStatementTask).filter(
        BankStatementTask.task_id == task_id,
        BankStatementTask.case_id == case_id
    ).first()

    if not task:
        return error_response(404, "任务不存在")

    # 计算已用时间
    elapsed_time = None
    if task.started_at:
        end_time = task.completed_at or datetime.now()
        elapsed_time = int((end_time - task.started_at).total_seconds())

    return success_response(
        data={
            "task_id": task.task_id,
            "status": task.status,
            "progress": task.progress,
            "current_step": task.current_step,
            "processed_files": task.processed_files,
            "total_files": task.file_count,
            "total_records": task.total_records,
            "success_records": task.success_records,
            "error_records": task.error_records,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "elapsed_time": elapsed_time,
            "error_message": task.error_message,
            "error_files": task.error_files
        }
    )


@router.get("/cases/{case_id}/bank-statements/tasks", summary="查询任务列表")
def get_task_list(
    case_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    查询案件的所有任务列表
    - 需要对案件有read权限
    """
    # 权限检查
    if current_user.role != "super_admin":
        if not check_case_permission(db, current_user.id, case_id, "read"):
            return error_response(403, "权限不足")

    # 构建查询
    query = db.query(BankStatementTask).filter(
        BankStatementTask.case_id == case_id
    )

    # 状态筛选
    if status:
        query = query.filter(BankStatementTask.status == status)

    # 总数
    total = query.count()

    # 分页
    tasks = query.order_by(desc(BankStatementTask.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for task in tasks:
        items.append({
            "id": task.id,
            "task_id": task.task_id,
            "status": task.status,
            "progress": task.progress,
            "file_count": task.file_count,
            "total_records": task.total_records,
            "created_at": task.created_at,
            "created_by": task.created_by
        })

    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.post("/cases/{case_id}/bank-statements/tasks/{task_id}/cancel", summary="取消任务")
def cancel_task(
    case_id: int,
    task_id: str,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    取消正在处理的任务
    - 需要对案件有write权限
    """
    # 权限检查
    if current_user.role != "super_admin":
        if not check_case_permission(db, current_user.id, case_id, "write"):
            return error_response(403, "权限不足")

    # 查询任务
    task = db.query(BankStatementTask).filter(
        BankStatementTask.task_id == task_id,
        BankStatementTask.case_id == case_id
    ).first()

    if not task:
        return error_response(404, "任务不存在")

    if task.status not in ["pending", "processing"]:
        return error_response(400, "任务已完成或已失败，无法取消")

    # 更新任务状态
    task.status = "cancelled"
    task.completed_at = datetime.now()
    db.commit()

    # TODO: 实际取消Celery任务
    # from backend.core.celery_app import celery_app
    # celery_app.control.revoke(task_id, terminate=True)

    return success_response(message="任务已取消")


@router.delete("/cases/{case_id}/bank-statements/tasks/{task_id}", summary="删除任务记录")
def delete_task(
    case_id: int,
    task_id: str,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    删除任务记录
    - 需要对案件有admin权限
    - 清理相关文件
    """
    # 权限检查
    if current_user.role != "super_admin":
        if not check_case_permission(db, current_user.id, case_id, "admin"):
            return error_response(403, "权限不足，需要管理员权限")

    # 查询任务
    task = db.query(BankStatementTask).filter(
        BankStatementTask.task_id == task_id,
        BankStatementTask.case_id == case_id
    ).first()

    if not task:
        return error_response(404, "任务不存在")

    if task.status == "processing":
        return error_response(400, "任务正在处理中，无法删除")

    # 清理文件
    file_service = FileStorageService()
    try:
        file_service.cleanup_task_files(case_id, task_id)
    except Exception as e:
        # 文件清理失败不影响记录删除
        pass

    # 删除任务记录
    db.delete(task)
    db.commit()

    return success_response(message="任务记录已删除")


@router.get("/cases/{case_id}/bank-statements/statistics", summary="获取导入统计")
def get_statistics(
    case_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """
    获取案件的银行流水导入统计
    - 汇总所有成功任务的数据
    """
    # 权限检查
    if current_user.role != "super_admin":
        if not check_case_permission(db, current_user.id, case_id, "read"):
            return error_response(403, "权限不足")

    # 查询所有成功的任务
    tasks = db.query(BankStatementTask).filter(
        BankStatementTask.case_id == case_id,
        BankStatementTask.status == "completed"
    ).all()

    # 汇总统计
    total_tasks = len(tasks)
    total_files = sum(task.file_count for task in tasks)
    total_records = sum(task.total_records for task in tasks)
    success_records = sum(task.success_records for task in tasks)
    error_records = sum(task.error_records for task in tasks)

    # 按类型汇总
    statistics = {
        "人员信息": 0,
        "账户信息": 0,
        "子账户信息": 0,
        "强制措施信息": 0,
        "交易明细": 0,
        "失败信息": 0
    }

    for task in tasks:
        if task.statistics:
            for key, value in task.statistics.items():
                if key in statistics:
                    statistics[key] += value

    return success_response(
        data={
            "total_tasks": total_tasks,
            "total_files": total_files,
            "total_records": total_records,
            "success_records": success_records,
            "error_records": error_records,
            "statistics": statistics
        }
    )
