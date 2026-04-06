# VehicleTestAI1 - 数据库初始化脚本

import sqlite3
import os
from datetime import datetime

# 数据库路径
DB_PATH = '/home/qw/.openclaw/workspace/VehicleTestAI1/backend/data/vehicletestai.db'

def init_database():
    """初始化数据库"""
    
    # 确保目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 正在创建数据库表...")
    
    # 创建项目表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建需求点表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requirements (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            priority TEXT,
            description TEXT,
            source TEXT,
            linked_reqs TEXT,
            reviewed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')
    
    # 创建测试策略表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_strategies (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')
    
    # 创建测试设计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_designs (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            requirement_id TEXT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')
    
    # 创建测试用例表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_cases (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            design_id TEXT,
            name TEXT NOT NULL,
            priority TEXT,
            steps TEXT,
            expected TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')
    
    # 创建测试日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_logs (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            signal TEXT,
            value TEXT,
            unit TEXT,
            pass BOOLEAN,
            timestamp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')
    
    # 创建 DBC 文件表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dbc_files (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            signal_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')
    
    # 创建 AI 历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_history (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            type TEXT NOT NULL,
            input TEXT,
            output TEXT,
            tokens_used INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_requirements_project ON requirements(project_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_strategies_project ON test_strategies(project_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_designs_project ON test_designs(project_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cases_project ON test_cases(project_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_project ON test_logs(project_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dbc_project ON dbc_files(project_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_project ON ai_history(project_id)')
    
    # 提交更改
    conn.commit()
    
    print("✅ 数据库表创建成功！")
    
    # 验证表结构
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"📊 已创建 {len(tables)} 个表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()

if __name__ == "__main__":
    init_database()
