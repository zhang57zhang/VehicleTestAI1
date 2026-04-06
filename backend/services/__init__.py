# -*- coding: utf-8 -*-
"""
车载控制器测试AI平台 - 服务模块
"""

from .ai_service import (
    AIServiceBase,
    MockAIService,
    MiniMaxService,
    get_ai_service,
    TestDocumentGenerator
)

__all__ = [
    'AIServiceBase',
    'MockAIService',
    'MiniMaxService',
    'get_ai_service',
    'TestDocumentGenerator'
]
