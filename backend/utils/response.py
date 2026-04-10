# -*- coding: utf-8 -*-
"""
VehicleTestAI - 统一API响应格式
提供标准化的API响应构建器，确保所有端点返回一致的格式
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json


class APIResponse:
    """统一API响应构建器
    
    标准响应格式:
    {
        "success": bool,
        "data": Any,          # 成功时返回的数据
        "error": {            # 失败时的错误信息
            "code": int,
            "message": str,
            "details": dict
        },
        "meta": {             # 元数据
            "timestamp": str,
            "request_id": str
        }
    }
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        meta: Optional[Dict] = None
    ) -> Dict:
        """构建成功响应
        
        Args:
            data: 返回的数据
            message: 成功消息
            meta: 额外的元数据
            
        Returns:
            标准化的成功响应字典
        """
        response = {
            "success": True,
            "message": message,
            "data": data,
            "meta": {
                "timestamp": datetime.now().isoformat(),
                **(meta or {})
            }
        }
        return response
    
    @staticmethod
    def error(
        message: str,
        error_code: int = 5000,
        details: Optional[Dict] = None,
        status_code: int = 500
    ) -> Dict:
        """构建错误响应
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
            status_code: HTTP状态码
            
        Returns:
            标准化的错误响应字典
        """
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {}
            },
            "meta": {
                "timestamp": datetime.now().isoformat()
            }
        }
        return response
    
    @staticmethod
    def paginated(
        items: List,
        total: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "查询成功"
    ) -> Dict:
        """构建分页响应
        
        Args:
            items: 当前页数据
            total: 总数量
            page: 当前页码
            page_size: 每页数量
            message: 成功消息
            
        Returns:
            包含分页信息的响应字典
        """
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        return APIResponse.success(
            data=items,
            message=message,
            meta={
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        )
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "创建成功",
        resource_type: str = None,
        resource_id: str = None
    ) -> Dict:
        """构建创建成功响应
        
        Args:
            data: 创建的资源数据
            message: 成功消息
            resource_type: 资源类型
            resource_id: 资源ID
            
        Returns:
            创建成功的响应字典
        """
        meta = {}
        if resource_type:
            meta["resource_type"] = resource_type
        if resource_id:
            meta["resource_id"] = resource_id
            
        return APIResponse.success(data=data, message=message, meta=meta)
    
    @staticmethod
    def updated(
        data: Any = None,
        message: str = "更新成功",
        changes: Optional[List[str]] = None
    ) -> Dict:
        """构建更新成功响应
        
        Args:
            data: 更新后的数据
            message: 成功消息
            changes: 变更的字段列表
            
        Returns:
            更新成功的响应字典
        """
        meta = {}
        if changes:
            meta["changes"] = changes
            
        return APIResponse.success(data=data, message=message, meta=meta)
    
    @staticmethod
    def deleted(
        resource_type: str = None,
        resource_id: str = None,
        message: str = "删除成功"
    ) -> Dict:
        """构建删除成功响应
        
        Args:
            resource_type: 资源类型
            resource_id: 资源ID
            message: 成功消息
            
        Returns:
            删除成功的响应字典
        """
        meta = {}
        if resource_type:
            meta["resource_type"] = resource_type
        if resource_id:
            meta["resource_id"] = resource_id
            
        return APIResponse.success(data=None, message=message, meta=meta)
    
    @staticmethod
    def not_found(
        resource_type: str,
        resource_id: str = None
    ) -> Dict:
        """构建资源未找到响应
        
        Args:
            resource_type: 资源类型
            resource_id: 资源ID
            
        Returns:
            资源未找到的响应字典
        """
        message = f"{resource_type}未找到"
        if resource_id:
            message = f"{resource_type} (ID: {resource_id}) 未找到"
            
        return APIResponse.error(
            message=message,
            error_code=1004,
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            },
            status_code=404
        )
    
    @staticmethod
    def validation_error(
        field: str,
        message: str,
        value: Any = None
    ) -> Dict:
        """构建验证错误响应
        
        Args:
            field: 验证失败的字段名
            message: 错误消息
            value: 提供的值
            
        Returns:
            验证错误的响应字典
        """
        return APIResponse.error(
            message=f"字段 '{field}' 验证失败: {message}",
            error_code=1003,
            details={
                "field": field,
                "reason": message,
                "provided_value": str(value) if value is not None else None
            },
            status_code=400
        )
    
    @staticmethod
    def batch_result(
        total: int,
        succeeded: int,
        failed: int,
        results: List[Dict],
        message: str = "批量操作完成"
    ) -> Dict:
        """构建批量操作结果响应
        
        Args:
            total: 总数量
            succeeded: 成功数量
            failed: 失败数量
            results: 详细结果列表
            message: 消息
            
        Returns:
            批量操作结果的响应字典
        """
        return APIResponse.success(
            data=results,
            message=message,
            meta={
                "batch": {
                    "total": total,
                    "succeeded": succeeded,
                    "failed": failed,
                    "success_rate": round(succeeded / total * 100, 2) if total > 0 else 0
                }
            }
        )


# 常用错误代码定义
class ErrorCode:
    """错误代码常量"""
    # 客户端错误 (1000-1999)
    INVALID_REQUEST = 1001
    MISSING_PARAMETER = 1002
    INVALID_PARAMETER = 1003
    RESOURCE_NOT_FOUND = 1004
    RESOURCE_ALREADY_EXISTS = 1005
    
    # 认证错误 (2000-2999)
    UNAUTHORIZED = 2001
    FORBIDDEN = 2002
    TOKEN_EXPIRED = 2003
    
    # 业务错误 (3000-3999)
    PROJECT_NOT_FOUND = 3001
    FILE_UPLOAD_FAILED = 3002
    AI_GENERATION_FAILED = 3003
    DATABASE_ERROR = 3004
    REQUIREMENT_PARSE_FAILED = 3005
    TEST_CASE_GENERATION_FAILED = 3006
    
    # 服务端错误 (5000-5999)
    INTERNAL_ERROR = 5000
    EXTERNAL_SERVICE_ERROR = 5001
    AI_SERVICE_UNAVAILABLE = 5002
