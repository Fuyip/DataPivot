"""
导入任务模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from database import Base


class ImportTask(Base):
    """导入任务表（存储在系统数据库）"""
    __tablename__ = 'import_task'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, nullable=False, comment='案件ID')
    task_type = Column(String(50), nullable=False, comment='任务类型：case_card/bank_statement')
    file_name = Column(String(255), comment='导入文件名')
    status = Column(String(20), default='pending', comment='任务状态: pending/processing/completed/failed')
    progress = Column(Float, default=0, comment='任务进度 0-100')
    current_step = Column(String(100), comment='当前步骤')
    total_count = Column(Integer, default=0, comment='总记录数')
    success_count = Column(Integer, default=0, comment='成功数')
    error_count = Column(Integer, default=0, comment='失败数')
    error_details = Column(Text, comment='错误详情JSON')
    error_message = Column(Text, comment='任务错误信息')
    task_ref = Column(String(100), comment='异步任务引用ID')
    storage_path = Column(String(500), comment='导入文件存储路径')
    created_by = Column(Integer, nullable=False, comment='创建人ID')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    started_at = Column(DateTime, comment='开始处理时间')
    completed_at = Column(DateTime, comment='完成时间')

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'task_type': self.task_type,
            'file_name': self.file_name,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'total_count': self.total_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'error_details': self.error_details,
            'error_message': self.error_message,
            'task_ref': self.task_ref,
            'storage_path': self.storage_path,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
