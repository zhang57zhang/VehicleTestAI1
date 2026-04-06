# -*- coding: utf-8 -*-
"""
VehicleTestAI1 - 数据库性能优化模块
提供索引优化、查询优化、连接池管理
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, func
from sqlalchemy.orm import Query
from contextlib import contextmanager
import time
import logging

logger = logging.getLogger(__name__)

# ==================== 数据库索引优化 ====================

def optimize_database_indexes(db):
    """优化数据库索引"""
    
    # 获取数据库连接
    with db.engine.connect() as conn:
        # 检查并创建索引
        
        # 项目表索引
        indexes = [
            # 项目表
            Index('idx_projects_name', 'projects', 'name'),
            Index('idx_projects_created', 'projects', 'created_at'),
            
            # 需求表
            Index('idx_requirements_project_category', 'requirements', 'project_id', 'category'),
            Index('idx_requirements_priority', 'requirements', 'priority'),
            Index('idx_requirements_created', 'requirements', 'created_at'),
            
            # 测试策略表
            Index('idx_strategies_project_created', 'test_strategies', 'project_id', 'created_at'),
            
            # 测试设计表
            Index('idx_designs_project_created', 'test_designs', 'project_id', 'created_at'),
            
            # 测试用例表
            Index('idx_cases_project_priority', 'test_cases', 'project_id', 'priority'),
            
            # 测试日志表
            Index('idx_logs_project_timestamp', 'test_logs', 'project_id', 'timestamp'),
            
            # AI 历史表
            Index('idx_ai_history_project_type', 'ai_history', 'project_id', 'type'),
            Index('idx_ai_history_created', 'ai_history', 'created_at'),
        ]
        
        for index in indexes:
            try:
                index.create(conn)
                logger.info(f"✅ 创建索引: {index.name}")
            except Exception as e:
                logger.warning(f"⚠️ 索引已存在或创建失败: {index.name} - {e}")

# ==================== 查询性能监控 ====================

class QueryPerformanceMonitor:
    """查询性能监控器"""
    
    def __init__(self):
        self.queries = []
        self.max_queries = 1000
        self.slow_query_threshold = 1.0  # 1 秒
    
    @contextmanager
    def monitor(self, query_name: str):
        """监控查询性能"""
        start_time = time.time()
        
        try:
            yield
        finally:
            elapsed_time = time.time() - start_time
            
            query_record = {
                'name': query_name,
                'time': elapsed_time,
                'timestamp': time.time(),
                'slow': elapsed_time > self.slow_query_threshold
            }
            
            self.queries.append(query_record)
            
            # 只保留最近的查询
            if len(self.queries) > self.max_queries:
                self.queries.pop(0)
            
            # 记录慢查询
            if query_record['slow']:
                logger.warning(f"🐢 慢查询: {query_name} 耗时 {elapsed_time:.2f}s")
            else:
                logger.debug(f"✓ 查询: {query_name} 耗时 {elapsed_time:.2f}s")
    
    def get_stats(self):
        """获取查询统计"""
        if not self.queries:
            return {
                'total_queries': 0,
                'avg_time': 0,
                'max_time': 0,
                'slow_queries': 0
            }
        
        times = [q['time'] for q in self.queries]
        
        return {
            'total_queries': len(self.queries),
            'avg_time': sum(times) / len(times),
            'max_time': max(times),
            'slow_queries': sum(1 for q in self.queries if q['slow'])
        }
    
    def get_slow_queries(self):
        """获取慢查询列表"""
        return [q for q in self.queries if q['slow']]

# 全局查询监控器
query_monitor = QueryPerformanceMonitor()

# ==================== 查询优化辅助函数 ====================

def paginate_query(query: Query, page: int = 1, per_page: int = 20):
    """分页查询优化"""
    with query_monitor.monitor(f'paginate_page_{page}'):
        # 计算偏移量
        offset = (page - 1) * per_page
        
        # 执行分页查询
        items = query.offset(offset).limit(per_page).all()
        
        # 获取总数（使用 count 优化）
        total = query.count()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }

def optimize_relationship_loading(query: Query, relationships: list):
    """优化关系加载（避免 N+1 查询）"""
    for rel in relationships:
        query = query.options(db.joinedload(rel))
    return query

# ==================== 连接池配置 ====================

def configure_connection_pool(app):
    """配置数据库连接池"""
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
    
    logger.info("✅ 数据库连接池已配置")

# ==================== 数据库健康检查 ====================

def check_database_health(db):
    """检查数据库健康状态"""
    try:
        # 执行简单查询
        with db.engine.connect() as conn:
            conn.execute('SELECT 1')
        
        return {
            'status': 'healthy',
            'pool_size': db.engine.pool.size(),
            'checked_out': db.engine.pool.checkedout(),
            'overflow': db.engine.pool.overflow()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
