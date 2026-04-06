# -*- coding: utf-8 -*-
"""
VehicleTestAI1 - 统一错误处理系统
提供错误分类、统一响应格式、错误追踪和日志记录
"""

import logging
import traceback
import uuid
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional, Callable

# ==================== 错误分类 ====================

class ErrorCategory:
    """错误分类"""
    CLIENT_ERROR = 'client_error'      # 客户端错误 (4xx)
    SERVER_ERROR = 'server_error'      # 服务端错误 (5xx)
    BUSINESS_ERROR = 'business_error'  # 业务逻辑错误
    VALIDATION_ERROR = 'validation_error'  # 验证错误
    AUTH_ERROR = 'auth_error'          # 认证错误
    NOT_FOUND = 'not_found'            # 资源未找到
    RATE_LIMIT = 'rate_limit'          # 速率限制
    EXTERNAL_ERROR = 'external_error'  # 外部服务错误

class ErrorCode:
    """错误代码定义"""
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
    INVALID_TOKEN = 2004
    
    # 业务错误 (3000-3999)
    PROJECT_NOT_FOUND = 3001
    FILE_UPLOAD_FAILED = 3002
    AI_GENERATION_FAILED = 3003
    DATABASE_ERROR = 3004
    
    # 服务端错误 (5000-5999)
    INTERNAL_ERROR = 5000
    EXTERNAL_SERVICE_ERROR = 5001
    DATABASE_CONNECTION_ERROR = 5002
    
    # 速率限制 (6000-6999)
    RATE_LIMIT_EXCEEDED = 6001

# ==================== 自定义异常 ====================

class VehicleTestAIError(Exception):
    """VehicleTestAI 基础异常"""
    
    def __init__(self, 
                 message: str, 
                 error_code: int = ErrorCode.INTERNAL_ERROR,
                 category: str = ErrorCategory.SERVER_ERROR,
                 status_code: int = 500,
                 details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.category = category
        self.status_code = status_code
        self.details = details or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        
        super().__init__(self.message)

class ValidationError(VehicleTestAIError):
    """验证错误"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_PARAMETER,
            category=ErrorCategory.VALIDATION_ERROR,
            status_code=400,
            details=details
        )

class NotFoundError(VehicleTestAIError):
    """资源未找到错误"""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} not found: {resource_id}",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            category=ErrorCategory.NOT_FOUND,
            status_code=404,
            details={'resource': resource, 'id': resource_id}
        )

class AuthenticationError(VehicleTestAIError):
    """认证错误"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            category=ErrorCategory.AUTH_ERROR,
            status_code=401
        )

class RateLimitError(VehicleTestAIError):
    """速率限制错误"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            category=ErrorCategory.RATE_LIMIT,
            status_code=429,
            details={'retry_after': retry_after}
        )

class ExternalServiceError(VehicleTestAIError):
    """外部服务错误"""
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} service error: {message}",
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            category=ErrorCategory.EXTERNAL_ERROR,
            status_code=503,
            details={'service': service}
        )

# ==================== 错误追踪器 ====================

class ErrorTracker:
    """错误追踪器"""
    
    def __init__(self):
        self.errors = []
        self.max_errors = 1000
    
    def track(self, error: VehicleTestAIError, request_info: Optional[Dict] = None):
        """追踪错误"""
        error_record = {
            'error_id': error.error_id,
            'error_code': error.error_code,
            'category': error.category,
            'message': error.message,
            'status_code': error.status_code,
            'timestamp': error.timestamp,
            'details': error.details,
            'request': request_info,
            'stack_trace': traceback.format_exc()
        }
        
        self.errors.append(error_record)
        
        # 只保留最近的错误
        if len(self.errors) > self.max_errors:
            self.errors.pop(0)
        
        return error_record
    
    def get_error(self, error_id: str) -> Optional[Dict]:
        """获取错误详情"""
        for error in self.errors:
            if error['error_id'] == error_id:
                return error
        return None
    
    def get_stats(self) -> Dict:
        """获取错误统计"""
        category_counts = {}
        for error in self.errors:
            category = error['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'total_errors': len(self.errors),
            'by_category': category_counts,
            'recent_errors': self.errors[-10:]  # 最近 10 个错误
        }
    
    def clear(self):
        """清空错误记录"""
        self.errors.clear()

# 全局错误追踪器
error_tracker = ErrorTracker()

# ==================== 日志系统 ====================

class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 如果没有处理器，添加一个
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        """记录日志"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        log_message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
        
        if level == 'DEBUG':
            self.logger.debug(log_message)
        elif level == 'INFO':
            self.logger.info(log_message)
        elif level == 'WARNING':
            self.logger.warning(log_message)
        elif level == 'ERROR':
            self.logger.error(log_message)
        elif level == 'CRITICAL':
            self.logger.critical(log_message)
    
    def debug(self, message: str, **kwargs):
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log('CRITICAL', message, **kwargs)

# 创建日志实例
import json
logger = StructuredLogger('VehicleTestAI')

# ==================== 统一错误响应 ====================

def create_error_response(error: VehicleTestAIError, include_trace: bool = False) -> Dict:
    """创建统一错误响应"""
    response = {
        'success': False,
        'error': {
            'id': error.error_id,
            'code': error.error_code,
            'category': error.category,
            'message': error.message,
            'timestamp': error.timestamp
        }
    }
    
    # 添加详细信息（如果有）
    if error.details:
        response['error']['details'] = error.details
    
    # 添加堆栈跟踪（开发环境）
    if include_trace:
        response['error']['trace'] = traceback.format_exc()
    
    return response

# ==================== 错误处理装饰器 ====================

def handle_errors(include_trace: bool = False):
    """错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except VehicleTestAIError as e:
                # 追踪错误
                request_info = {
                    'function': func.__name__,
                    'args': str(args)[:200],  # 限制长度
                    'kwargs': str(kwargs)[:200]
                }
                error_tracker.track(e, request_info)
                
                # 记录日志
                logger.error(
                    f"VehicleTestAI error in {func.__name__}",
                    error_id=e.error_id,
                    error_code=e.error_code,
                    message=e.message
                )
                
                # 返回错误响应
                response = create_error_response(e, include_trace)
                return response, e.status_code
            
            except Exception as e:
                # 未知错误，转换为 VehicleTestAIError
                vta_error = VehicleTestAIError(
                    message=str(e),
                    error_code=ErrorCode.INTERNAL_ERROR,
                    category=ErrorCategory.SERVER_ERROR,
                    status_code=500
                )
                
                # 追踪错误
                request_info = {
                    'function': func.__name__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                }
                error_tracker.track(vta_error, request_info)
                
                # 记录日志
                logger.critical(
                    f"Unexpected error in {func.__name__}",
                    error_id=vta_error.error_id,
                    error=str(e),
                    trace=traceback.format_exc()
                )
                
                # 返回错误响应
                response = create_error_response(vta_error, include_trace)
                return response, 500
        
        return wrapper
    return decorator

# ==================== 降级策略 ====================

class FallbackStrategy:
    """降级策略"""
    
    @staticmethod
    def ai_service_fallback(func: Callable) -> Callable:
        """AI 服务降级"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"AI service failed, using fallback",
                    function=func.__name__,
                    error=str(e)
                )
                # 返回默认或缓存的结果
                return {
                    'success': False,
                    'error': 'AI service temporarily unavailable',
                    'fallback': True
                }
        return wrapper
    
    @staticmethod
    def database_fallback(func: Callable) -> Callable:
        """数据库降级"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"Database failed, using cache",
                    function=func.__name__,
                    error=str(e)
                )
                # 从缓存返回数据
                return {
                    'success': False,
                    'error': 'Database temporarily unavailable',
                    'fallback': True
                }
        return wrapper

# ==================== 工具函数 ====================

def get_error_stats() -> Dict:
    """获取错误统计"""
    return error_tracker.get_stats()

def get_error_by_id(error_id: str) -> Optional[Dict]:
    """根据 ID 获取错误详情"""
    return error_tracker.get_error(error_id)

def clear_error_tracker():
    """清空错误追踪器"""
    error_tracker.clear()
    logger.info("Error tracker cleared")
