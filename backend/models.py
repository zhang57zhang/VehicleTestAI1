# VehicleTestAI1 - 数据库模型（SQLAlchemy）

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Project(db.Model):
    """项目模型"""
    __tablename__ = 'projects'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    requirements = db.relationship('Requirement', backref='project', lazy=True, cascade='all, delete-orphan')
    test_strategies = db.relationship('TestStrategy', backref='project', lazy=True, cascade='all, delete-orphan')
    test_designs = db.relationship('TestDesign', backref='project', lazy=True, cascade='all, delete-orphan')
    test_cases = db.relationship('TestCase', backref='project', lazy=True, cascade='all, delete-orphan')
    test_logs = db.relationship('TestLog', backref='project', lazy=True, cascade='all, delete-orphan')
    dbc_files = db.relationship('DBCFile', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Requirement(db.Model):
    """需求点模型"""
    __tablename__ = 'requirements'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String)
    priority = db.Column(db.String)
    description = db.Column(db.Text)
    source = db.Column(db.String)
    linked_reqs = db.Column(db.Text)  # JSON string
    reviewed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'priority': self.priority,
            'description': self.description,
            'source': self.source,
            'linkedReqs': self.linked_reqs,
            'reviewed': self.reviewed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TestStrategy(db.Model):
    """测试策略模型"""
    __tablename__ = 'test_strategies'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TestDesign(db.Model):
    """测试设计模型"""
    __tablename__ = 'test_designs'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False)
    requirement_id = db.Column(db.String, db.ForeignKey('requirements.id'))
    name = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'requirement_id': self.requirement_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TestCase(db.Model):
    """测试用例模型"""
    __tablename__ = 'test_cases'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False)
    design_id = db.Column(db.String, db.ForeignKey('test_designs.id'))
    name = db.Column(db.String, nullable=False)
    priority = db.Column(db.String)
    steps = db.Column(db.Text)
    expected = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'priority': self.priority,
            'steps': self.steps,
            'expected': self.expected,
            'design_id': self.design_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TestLog(db.Model):
    """测试日志模型"""
    __tablename__ = 'test_logs'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False)
    signal = db.Column(db.String)
    value = db.Column(db.String)
    unit = db.Column(db.String)
    pass_ = db.Column('pass', db.Boolean)
    timestamp = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'signal': self.signal,
            'value': self.value,
            'unit': self.unit,
            'pass': self.pass_,
            'timestamp': self.timestamp,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DBCFile(db.Model):
    """DBC 文件模型"""
    __tablename__ = 'dbc_files'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    path = db.Column(db.String, nullable=False)
    signal_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'signal_count': self.signal_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AIHistory(db.Model):
    """AI 历史模型"""
    __tablename__ = 'ai_history'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'))
    type = db.Column(db.String, nullable=False)
    input = db.Column(db.Text)
    output = db.Column(db.Text)
    tokens_used = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'input': self.input,
            'output': self.output,
            'tokens_used': self.tokens_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
