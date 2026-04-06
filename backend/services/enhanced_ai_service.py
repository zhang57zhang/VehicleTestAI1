# -*- coding: utf-8 -*-
"""
车载控制器测试AI平台 - 增强 AI 服务模块
支持 Token 统计、错误处理、重试机制、缓存
"""

import time
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from functools import wraps

# ==================== Token 统计装饰器 ====================

class TokenCounter:
    """Token 计数器"""
    
    def __init__(self):
        self.total_tokens = 0
        self.total_calls = 0
        self.total_cost = 0.0
        self.history = []
    
    def record(self, tokens: int, model: str, call_type: str):
        """记录 Token 使用"""
        self.total_tokens += tokens
        self.total_calls += 1
        
        # 计算成本（基于智谱 AI 定价）
        cost_per_1k_tokens = {
            'glm-4-plus': 0.05,  # ¥0.05/千tokens
            'glm-4': 0.01,       # ¥0.01/千tokens
        }
        cost = (tokens / 1000) * cost_per_1k_tokens.get(model, 0.05)
        self.total_cost += cost
        
        # 记录历史
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'call_type': call_type,
            'tokens': tokens,
            'cost': cost,
            'model': model
        })
        
        # 只保留最近 100 条记录
        if len(self.history) > 100:
            self.history.pop(0)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_tokens': self.total_tokens,
            'total_calls': self.total_calls,
            'total_cost': round(self.total_cost, 4),
            'avg_tokens_per_call': round(self.total_tokens / max(self.total_calls, 1), 2),
            'history_count': len(self.history)
        }

# 全局 Token 计数器
token_counter = TokenCounter()

def count_tokens(call_type: str):
    """Token 计数装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            try:
                result = func(self, *args, **kwargs)
                elapsed_time = time.time() - start_time
                
                # 估算 Token 数量（基于字符数，中文约 1.5 字符/token）
                approx_tokens = int(len(result) / 1.5) if isinstance(result, str) else 0
                
                # 记录统计
                token_counter.record(
                    tokens=approx_tokens,
                    model=getattr(self, 'model', 'unknown'),
                    call_type=call_type
                )
                
                return result
            except Exception as e:
                # 错误也记录
                token_counter.record(
                    tokens=0,
                    model=getattr(self, 'model', 'unknown'),
                    call_type=f'{call_type}_error'
                )
                raise
        return wrapper
    return decorator

# ==================== 重试机制 ====================

def retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff ** attempt)
                        print(f"⚠️ 第 {attempt + 1} 次失败，{wait_time}秒后重试: {str(e)}")
                        time.sleep(wait_time)
            
            # 所有重试都失败
            print(f"❌ 重试 {max_retries} 次后仍失败: {str(last_exception)}")
            raise last_exception
        return wrapper
    return decorator

# ==================== 响应缓存 ====================

class ResponseCache:
    """AI 响应缓存"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def _hash_key(self, prompt: str, max_tokens: int) -> str:
        """生成缓存键"""
        key_str = f"{prompt}:{max_tokens}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prompt: str, max_tokens: int) -> Optional[str]:
        """获取缓存"""
        key = self._hash_key(prompt, max_tokens)
        return self.cache.get(key)
    
    def set(self, prompt: str, max_tokens: int, response: str):
        """设置缓存"""
        key = self._hash_key(prompt, max_tokens)
        
        # 如果缓存满了，删除最早的
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size
        }

# 全局缓存实例
response_cache = ResponseCache()

# ==================== 增强 AI 服务 ====================

class EnhancedAIService:
    """增强 AI 服务基类"""
    
    def __init__(self, api_key: str = None, model: str = 'unknown'):
        self.api_key = api_key
        self.model = model
        self.cache_enabled = True
        self.retry_enabled = True
        self.max_retries = 3
    
    @retry(max_retries=3, delay=1.0, backoff=2.0)
    @count_tokens('generate')
    def generate_with_cache(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成内容（带缓存）"""
        # 检查缓存
        if self.cache_enabled:
            cached = response_cache.get(prompt, max_tokens)
            if cached:
                print(f"✅ 使用缓存响应")
                return cached['response']
        
        # 调用实际生成方法
        response = self.generate(prompt, max_tokens)
        
        # 保存到缓存
        if self.cache_enabled:
            response_cache.set(prompt, max_tokens, response)
        
        return response
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成内容 - 子类实现"""
        raise NotImplementedError
    
    def analyze(self, content: str) -> Dict:
        """分析内容 - 子类实现"""
        raise NotImplementedError
    
    def get_token_stats(self) -> Dict:
        """获取 Token 统计"""
        return token_counter.get_stats()
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return response_cache.get_stats()
    
    def enable_cache(self, enabled: bool = True):
        """启用/禁用缓存"""
        self.cache_enabled = enabled
    
    def clear_cache(self):
        """清空缓存"""
        response_cache.clear()

# ==================== 智谱 AI 增强 服务 ====================

class EnhancedGLMService(EnhancedAIService):
    """增强智谱 AI 服务"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, 'glm-4-plus')
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=api_key)
            print("✅ 智谱 AI 客户端初始化成功")
        except Exception as e:
            print(f"❌ 智谱 AI 客户端初始化失败: {e}")
            self.client = None
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成内容"""
        if not self.client:
            raise Exception("智谱 AI 客户端未初始化")
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            
            # 记录实际使用的 Token 数
            if hasattr(response, 'usage') and hasattr(response.usage, 'total_tokens'):
                actual_tokens = response.usage.total_tokens
                token_counter.record(
                    tokens=actual_tokens,
                    model=self.model,
                    call_type='generate_actual'
                )
            
            return content
            
        except Exception as e:
            raise Exception(f"智谱 AI 生成失败: {str(e)}")
    
    def analyze(self, content: str) -> Dict:
        """分析内容"""
        prompt = f"请分析以下内容并提取关键信息：\n\n{content}"
        result = self.generate_with_cache(prompt, max_tokens=1000)
        
        return {
            'summary': result[:200] + '...' if len(result) > 200 else result,
            'keywords': [],  # TODO: 实现关键词提取
            'sentiment': 'neutral'  # TODO: 实现情感分析
        }

# ==================== 工厂函数 ====================

def get_enhanced_ai_service(service_type: str = 'glm', api_key: str = None) -> EnhancedAIService:
    """获取增强 AI 服务实例"""
    if service_type == 'glm' and api_key:
        return EnhancedGLMService(api_key)
    else:
        # 降级到 Mock 服务
        from services.ai_service import MockAIService
        print("⚠️ 降级到 Mock AI 服务")
        return MockAIService(api_key)

# ==================== 工具函数 ====================

def get_ai_stats() -> Dict:
    """获取 AI 统计信息"""
    return {
        'token_stats': token_counter.get_stats(),
        'cache_stats': response_cache.get_stats()
    }

def clear_ai_cache():
    """清空 AI 缓存"""
    response_cache.clear()
    print("✅ AI 缓存已清空")

def reset_ai_stats():
    """重置 AI 统计"""
    global token_counter
    token_counter = TokenCounter()
    print("✅ AI 统计已重置")
