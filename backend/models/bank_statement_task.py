"""
银行流水处理任务模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base


class BankStatementTask(Base):
    """银行流水处理任务表 - 存储在datapivot数据库"""
    __tablename__ = "bank_statement_tasks"

    id = Column(Integer, primary_key=True, index=True, comment="任务ID")
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, index=True, comment="案件ID")
    task_id = Column(String(100), unique=True, nullable=False, index=True, comment="Celery任务ID")
    template_id = Column(Integer, ForeignKey("import_rule_templates.id"), nullable=True, index=True, comment="使用的规则模板ID")

    # 任务信息
    status = Column(String(20), default="pending", comment="任务状态: pending/processing/completed/failed/cancelled")
    task_type = Column(String(20), default="upload", comment="任务类型: upload/reprocess")

    # 文件信息
    file_count = Column(Integer, default=0, comment="上传的文件数量")
    file_names = Column(JSON, comment="文件名列表")
    file_size_total = Column(Float, default=0, comment="总文件大小（MB）")

    # 进度信息
    progress = Column(Float, default=0, comment="进度 0-100")
    current_step = Column(String(100), comment="当前步骤描述")
    processed_files = Column(Integer, default=0, comment="已处理文件数")

    # 处理结果统计
    total_records = Column(Integer, default=0, comment="总记录数")
    success_records = Column(Integer, default=0, comment="成功记录数")
    error_records = Column(Integer, default=0, comment="错误记录数")
    error_files = Column(JSON, comment="错误文件列表")

    # 详细统计（按数据类型）
    statistics = Column(JSON, comment="统计信息: {人员信息: 100, 账户信息: 200, ...}")

    # 错误信息
    error_message = Column(Text, comment="错误详情")

    # 时间戳
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    started_at = Column(DateTime(timezone=True), comment="开始处理时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")

    # 文件路径（用于清理）
    storage_path = Column(String(500), comment="文件存储路径")

    def __repr__(self):
        return f"<BankStatementTask(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"
