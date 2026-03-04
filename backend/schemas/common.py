"""
通用响应模型
"""
from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    code: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {}
            }
        }


def success_response(data: Any = None, message: str = "success") -> dict:
    """
    成功响应

    Args:
        data: 响应数据
        message: 响应消息

    Returns:
        dict: 响应字典
    """
    return {
        "code": 200,
        "message": message,
        "data": data
    }


def error_response(code: int, message: str, data: Any = None) -> dict:
    """
    错误响应

    Args:
        code: 错误码
        message: 错误消息
        data: 额外数据

    Returns:
        dict: 响应字典
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }
