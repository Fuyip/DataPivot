"""
银行流水相关的Schema定义
"""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class BankStatementUploadResponse(BaseModel):
    """上传响应"""
    task_id: str
    message: str
    file_count: int
    estimated_time: Optional[int] = None  # 预估处理时间（秒）


class TaskProgress(BaseModel):
    """任务进度"""
    task_id: str
    status: str  # pending/processing/completed/failed/cancelled
    progress: float  # 0-100
    current_step: Optional[str] = None
    processed_files: int
    total_files: int

    # 统计信息
    total_records: int = 0
    success_records: int = 0
    error_records: int = 0

    # 时间信息
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    elapsed_time: Optional[int] = None  # 已用时间（秒）

    # 错误信息
    error_message: Optional[str] = None
    error_files: Optional[List[str]] = None

    class Config:
        from_attributes = True


class TaskStatistics(BaseModel):
    """任务统计详情"""
    task_id: str
    status: str

    # 文件统计
    file_count: int
    file_size_total: float
    processed_files: int
    error_files: List[str] = []

    # 数据统计（按类型）
    statistics: Dict[str, int] = {}  # {"人员信息": 100, "账户信息": 200, ...}

    # 总体统计
    total_records: int
    success_records: int
    error_records: int

    # 时间统计
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[int] = None  # 处理耗时（秒）

    class Config:
        from_attributes = True


class TaskListItem(BaseModel):
    """任务列表项"""
    id: int
    task_id: str
    status: str
    progress: float
    file_count: int
    total_records: int
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True
