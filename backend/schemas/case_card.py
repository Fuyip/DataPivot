from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CaseCardBase(BaseModel):
    """案件银行卡基础模型"""
    card_no: str = Field(..., description="卡号")
    bank_name: Optional[str] = Field(None, description="银行名称")
    card_type: Optional[str] = Field(None, description="卡类型")
    source: Optional[str] = Field(None, description="来源信息")
    user_id: Optional[str] = Field(None, description="用户ID")
    batch: Optional[int] = Field(None, description="批次")
    is_in_bg: Optional[int] = Field(None, description="是否在后台")
    is_main: Optional[int] = Field(None, description="是否为主卡")


class CaseCardCreate(CaseCardBase):
    """创建案件银行卡"""
    pass


class CaseCardUpdate(BaseModel):
    """更新案件银行卡"""
    bank_name: Optional[str] = None
    card_type: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[str] = None
    batch: Optional[int] = None
    is_in_bg: Optional[int] = None
    is_main: Optional[int] = None


class CaseCardResponse(CaseCardBase):
    """案件银行卡响应"""
    id: int
    case_no: str
    add_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseCardListResponse(BaseModel):
    """案件银行卡列表响应"""
    items: list[CaseCardResponse]
    total: int
    page: int
    page_size: int
