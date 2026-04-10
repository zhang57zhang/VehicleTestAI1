# -*- coding: utf-8 -*-
"""
VehicleTestAI - 数据库初始化脚本
创建所有表并添加必要的初始数据
"""

import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, ActivityState
from utils.config import get_config

def init_database():
    """初始化数据库"""
    config = get_config()
    
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = config.database.uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("[OK] Database tables created")
        
        # 验证表结构
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"[OK] Tables: {', '.join(tables)}")
        
        return True


def migrate_database():
    """数据库迁移 - 添加新表"""
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data", "vehicletestai.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    with app.app_context():
        # 检查并创建新表
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # 需要确保存在的表
        required_tables = [
            'activity_states',
            'test_executions'
        ]
        
        for table in required_tables:
            if table not in existing_tables:
                print(f"[MIGRATE] Creating table: {table}")
        
        # 创建所有缺失的表
        db.create_all()
        print("[OK] Migration completed")


if __name__ == "__main__":
    print("Initializing VehicleTestAI database...")
    init_database()
    print("Done!")
