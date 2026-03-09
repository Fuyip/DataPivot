from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class BankInfoChangeRequest(Base):
    """银行信息变更申请表 - 存储在 datapivot 数据库"""
    __tablename__ = "bank_info_change_requests"

    id = Column(Integer, primary_key=True, index=True, comment="变更申请ID")
    table_type = Column(String(20), nullable=False, comment="表类型: bank_bin/sy_bank")
    change_type = Column(String(20), nullable=False, comment="变更类型: create/update/delete")

    # 原始数据（JSON格式存储）
    old_data = Column(Text, comment="原始数据（JSON）")
    # 新数据（JSON格式存储）
    new_data = Column(Text, nullable=False, comment="新数据（JSON）")

    # 变更说明
    reason = Column(String(500), comment="变更原因")

    # 状态
    status = Column(String(20), default="pending", comment="状态: pending/approved/rejected/executed")

    # 申请人
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="申请人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="申请时间")

    # 审批人
    reviewed_by = Column(Integer, ForeignKey("users.id"), comment="审批人ID")
    reviewed_at = Column(DateTime(timezone=True), comment="审批时间")
    review_comment = Column(String(500), comment="审批意见")

    # 执行时间
    executed_at = Column(DateTime(timezone=True), comment="执行时间")

    def __repr__(self):
        return f"<BankInfoChangeRequest(id={self.id}, table={self.table_type}, type={self.change_type}, status={self.status})>"
