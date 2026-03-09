from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== BankBin 相关 Schema ====================

class BankBinBase(BaseModel):
    """BankBin 基础模型"""
    bin: str = Field(..., description="BIN码")
    bin_len: int = Field(..., description="BIN长度")
    card_len: int = Field(..., description="卡长度")
    bank_name: str = Field(..., description="银行名称")


class BankBinCreate(BankBinBase):
    """创建 BankBin"""
    pass


class BankBinUpdate(BankBinBase):
    """更新 BankBin"""
    pass


class BankBinResponse(BankBinBase):
    """BankBin 响应"""
    id: Optional[int] = None

    class Config:
        from_attributes = True


# ==================== SyBank 相关 Schema ====================

class SyBankBase(BaseModel):
    """SyBank 基础模型"""
    from_bank: str = Field(..., description="原始银行名称")
    to_bank: str = Field(..., description="标准银行名称")
    sys: str = Field(default="jz", description="系统标识")


class SyBankCreate(SyBankBase):
    """创建 SyBank"""
    pass


class SyBankUpdate(SyBankBase):
    """更新 SyBank"""
    pass


class SyBankResponse(SyBankBase):
    """SyBank 响应"""
    id: Optional[int] = None

    class Config:
        from_attributes = True


# ==================== 变更申请相关 Schema ====================

class ChangeRequestCreate(BaseModel):
    """创建变更申请"""
    table_type: str = Field(..., description="表类型: bank_bin/sy_bank")
    change_type: str = Field(..., description="变更类型: create/update/delete")
    old_data: Optional[str] = Field(None, description="原始数据（JSON）")
    new_data: str = Field(..., description="新数据（JSON）")
    reason: Optional[str] = Field(None, description="变更原因")
    direct_execute: bool = Field(default=False, description="是否直接执行（超级管理员）")


class ChangeRequestResponse(BaseModel):
    """变更申请响应"""
    id: int
    table_type: str
    change_type: str
    old_data: Optional[str]
    new_data: str
    reason: Optional[str]
    status: str
    created_by: int
    created_at: datetime
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    review_comment: Optional[str]
    executed_at: Optional[datetime]

    # 关联信息
    creator_name: Optional[str] = None
    reviewer_name: Optional[str] = None

    class Config:
        from_attributes = True


class ChangeRequestReview(BaseModel):
    """审批变更申请"""
    review_comment: Optional[str] = Field(None, description="审批意见")


class ChangeRequestList(BaseModel):
    """变更申请列表响应"""
    items: List[ChangeRequestResponse]
    total: int
    page: int
    page_size: int


# ==================== 操作请求 Schema ====================

class BankBinOperationRequest(BaseModel):
    """BankBin 操作请求"""
    data: BankBinBase
    reason: Optional[str] = Field(None, description="变更原因")
    direct_execute: bool = Field(default=False, description="是否直接执行（超级管理员）")


class SyBankOperationRequest(BaseModel):
    """SyBank 操作请求"""
    data: SyBankBase
    reason: Optional[str] = Field(None, description="变更原因")
    direct_execute: bool = Field(default=False, description="是否直接执行（超级管理员）")


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., description="要删除的ID列表")
    reason: Optional[str] = Field(None, description="删除原因")
    direct_execute: bool = Field(default=False, description="是否直接执行（超级管理员）")


# ==================== 导入相关 Schema ====================

class ImportResult(BaseModel):
    """导入结果"""
    success_count: int = Field(..., description="成功数量")
    error_count: int = Field(..., description="失败数量")
    errors: List[str] = Field(default=[], description="错误信息列表")
    request_id: Optional[int] = Field(None, description="变更申请ID（如果需要审批）")


# ==================== 查询参数 Schema ====================

class BankBinQueryParams(BaseModel):
    """BankBin 查询参数"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    bin: Optional[str] = None
    bank_name: Optional[str] = None
    bin_len: Optional[int] = None
    card_len: Optional[int] = None


class SyBankQueryParams(BaseModel):
    """SyBank 查询参数"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    from_bank: Optional[str] = None
    to_bank: Optional[str] = None
    sys: Optional[str] = None


class ChangeRequestQueryParams(BaseModel):
    """变更申请查询参数"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    status: Optional[str] = None
    table_type: Optional[str] = None
    change_type: Optional[str] = None
    created_by: Optional[int] = None
