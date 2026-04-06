# -*- coding: utf-8 -*-
"""
VehicleTestAI1 - API 响应缓存系统
提供内存缓存、缓存策略、缓存失效管理
"""

import time
import hashlib
import json
from typing import Any, Optional, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# ==================== 内存缓存 ====================

class MemoryCache:
    """内存缓存（带 TTL）"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def _hash_key(self, key: str) -> str:
        """生成缓存键的哈希"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        hashed_key = self._hash_key(key)
        
        if hashed_key in self.cache:
            item = self.cache[hashed_key]
            
            # 检查是否过期
            if time.time() < item['expires']:
                self.hits += 1
                logger.debug(f"✅ 缓存命中: {key}")
                return item['value']
            else:
                # 过期，删除
                del self.cache[hashed_key]
        
        self.misses += 1
        logger.debug(f"❌ 缓存未命中: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存"""
        hashed_key = self._hash_key(key)
        
        # 如果缓存满了，删除最早的
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        expires = time.time() + (ttl or self.default_ttl)
        
        self.cache[hashed_key] = {
            'key': key,
            'value': value,
            'expires': expires,
            'created': time.time()
        }
        
        logger.debug(f"✓ 缓存已设置: {key} (TTL: {ttl or self.default_ttl}s)")
    
    def delete(self, key: str):
        """删除缓存"""
        hashed_key = self._hash_key(key)
        if hashed_key in self.cache:
            del self.cache[hashed_key]
            logger.debug(f"✗ 缓存已删除: {key}")
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("🗑️ 缓存已清空")
    
    def _evict_oldest(self):
        """删除最早的缓存项"""
        if not self.cache:
            return
        
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['created'])
        del self.cache[oldest_key]
        logger.debug("🗑️ 已删除最早的缓存项")
    
    def cleanup_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            k for k, v in self.cache.items()
            if v['expires'] < current_time
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"🗑️ 已清理 {len(expired_keys)} 个过期缓存")
    
    def get_stats(self):
        """获取缓存统计"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }

# 全局缓存实例
api_cache = MemoryCache(max_size=500, default_ttl=300)  # 5 分钟 TTL

# ==================== 缓存装饰器 ====================

def cache_response(ttl: int = 300, key_prefix: str = ''):
    """API 响应缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_result = api_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            api_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# ==================== 缓存管理 API ====================

def get_cache_stats():
    """获取缓存统计"""
    return api_cache.get_stats()

def clear_cache():
    """清空缓存"""
    api_cache.clear()

def cleanup_cache():
    """清理过期缓存"""
    api_cache.cleanup_expired()

# ==================== 项目相关缓存 ====================

class ProjectCache:
    """项目相关缓存管理"""
    
    @staticmethod
    def get_project(project_id: str):
        """获取项目缓存"""
        key = f"project:{project_id}"
        return api_cache.get(key)
    
    @staticmethod
    def set_project(project_id: str, project_data: dict, ttl: int = 600):
        """设置项目缓存"""
        key = f"project:{project_id}"
        api_cache.set(key, project_data, ttl)
    
    @staticmethod
    def invalidate_project(project_id: str):
        """使项目缓存失效"""
        keys_to_delete = [
            f"project:{project_id}",
            f"project_requirements:{project_id}",
            f"project_strategies:{project_id}",
            f"project_designs:{project_id}"
        ]
        
        for key in keys_to_delete:
            api_cache.delete(key)
        
        logger.info(f"🗑️ 已清除项目 {project_id} 的所有缓存")

# ==================== AI 响应缓存 ====================

class AICache:
    """AI 响应缓存"""
    
    @staticmethod
    def get_ai_response(prompt_hash: str):
        """获取 AI 响应缓存"""
        key = f"ai_response:{prompt_hash}"
        return api_cache.get(key)
    
    @staticmethod
    def set_ai_response(prompt_hash: str, response: str, ttl: int = 3600):
        """设置 AI 响应缓存（1 小时）"""
        key = f"ai_response:{prompt_hash}"
        api_cache.set(key, response, ttl)
    
    @staticmethod
    def hash_prompt(prompt: str) -> str:
        """生成提示词哈希"""
        return hashlib.md5(prompt.encode()).hexdigest()
