"""
导入任务模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class ImportTask(Base):
    """导入任务表（存储在系统数据库）"""
    __tablename__ = 'import_task'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, nullable=False, comment='案件ID')
    task_type = Column(String(50), nullable=False, comment='任务类型：case_card/bank_statement')
    file_name = Column(String(255), comment='导入文件名')
    total_count = Column(Integer, default=0, comment='总记录数')
    success_count = Column(Integer, default=0, comment='成功数')
    error_count = Column(Integer, default=0, comment='失败数')
    error_details = Column(Text, comment='错误详情JSON')
    created_by = Column(Integer, nullable=False, comment='创建人ID')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'task_type': self.task_type,
            'file_name': self.file_name,
            'total_count': self.total_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'error_details': self.error_details,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
