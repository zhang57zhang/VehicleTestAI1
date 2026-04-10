# VehicleTestAI1 - 数据库模型（SQLAlchemy）
# 优化版本：添加索引、改进关系、支持测试活动流程

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Project(db.Model):
    """项目模型
    
    对应测试活动：所有活动的容器
    """
    __tablename__ = 'projects'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')  # active, archived, deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    requirements = db.relationship('Requirement', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    test_strategies = db.relationship('TestStrategy', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    test_designs = db.relationship('TestDesign', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    test_cases = db.relationship('TestCase', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    test_logs = db.relationship('TestLog', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    dbc_files = db.relationship('DBCFile', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    activity_states = db.relationship('ActivityState', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_statistics(self):
        """获取项目统计信息"""
        return {
            'requirements_count': self.requirements.count(),
            'strategies_count': self.test_strategies.count(),
            'designs_count': self.test_designs.count(),
            'testcases_count': self.test_cases.count(),
            'logs_count': self.test_logs.count()
        }


class Requirement(db.Model):
    """需求点模型
    
    对应测试活动：RA (Requirement Analysis)
    活动代码：ACT-RA-*
    """
    __tablename__ = 'requirements'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False, index=True)
    name = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), index=True)  # 功能需求/性能需求/安全需求/接口需求
    priority = db.Column(db.String(10), index=True)  # P0/P1/P2/P3
    description = db.Column(db.Text)
    source = db.Column(db.String(50))  # AI解析/手动添加
    linked_reqs = db.Column(db.Text)  # JSON string
    reviewed = db.Column(db.Boolean, default=False, index=True)
    asil_level = db.Column(db.String(10))  # ASIL A/B/C/D
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    test_designs = db.relationship('TestDesign', backref='requirement', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'category': self.category,
            'priority': self.priority,
            'description': self.description,
            'source': self.source,
            'linkedReqs': self.linked_reqs,
            'reviewed': self.reviewed,
            'asil_level': self.asil_level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TestStrategy(db.Model):
    """测试策略模型
    
    对应测试活动：TS (Test Strategy)
    活动代码：ACT-TS-*
    """
    __tablename__ = 'test_strategies'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    test_environment = db.Column(db.String(50))  # HIL/SIL/DIL
    status = db.Column(db.String(50), default='draft')  # draft/reviewed/approved
    version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'content': self.content,
            'test_environment': self.test_environment,
            'status': self.status,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TestDesign(db.Model):
    """测试设计模型
    
    对应测试活动：TD (Test Design)
    活动代码：ACT-TD-*
    """
    __tablename__ = 'test_designs'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False, index=True)
    requirement_id = db.Column(db.String, db.ForeignKey('requirements.id'), index=True)
    name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    design_type = db.Column(db.String(50))  # functional/performance/safety
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'requirement_id': self.requirement_id,
            'name': self.name,
            'content': self.content,
            'design_type': self.design_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TestCase(db.Model):
    """测试用例模型
    
    对应测试活动：TC (Test Cases)
    活动代码：ACT-TC-*
    """
    __tablename__ = 'test_cases'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False, index=True)
    design_id = db.Column(db.String, db.ForeignKey('test_designs.id'), index=True)
    name = db.Column(db.String(500), nullable=False)
    module = db.Column(db.String(100), index=True)  # 测试模块
    priority = db.Column(db.String(10), index=True)
    test_type = db.Column(db.String(50))  # functional/performance/safety/interface
    precondition = db.Column(db.Text)
    steps = db.Column(db.Text)
    input_data = db.Column(db.Text)
    expected = db.Column(db.Text)
    auto = db.Column(db.Boolean, default=False)  # 是否可自动化
    executed = db.Column(db.Boolean, default=False, index=True)
    passed = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'design_id': self.design_id,
            'name': self.name,
            'module': self.module,
            'priority': self.priority,
            'test_type': self.test_type,
            'precondition': self.precondition,
            'steps': self.steps,
            'input': self.input_data,
            'expected': self.expected,
            'auto': self.auto,
            'executed': self.executed,
            'passed': self.passed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TestLog(db.Model):
    """测试日志模型
    
    对应测试活动：TL (Test Logs)
    活动代码：ACT-TL-*
    """
    __tablename__ = 'test_logs'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False, index=True)
    test_case_id = db.Column(db.String, db.ForeignKey('test_cases.id'), index=True)
    signal = db.Column(db.String(200), index=True)
    value = db.Column(db.Text)
    unit = db.Column(db.String(50))
    pass_ = db.Column('pass', db.Boolean, index=True)
    timestamp = db.Column(db.String(50), index=True)
    log_type = db.Column(db.String(50))  # execution/analysis/error
    raw_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'test_case_id': self.test_case_id,
            'signal': self.signal,
            'value': self.value,
            'unit': self.unit,
            'pass': self.pass_,
            'timestamp': self.timestamp,
            'log_type': self.log_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DBCFile(db.Model):
    """DBC 文件模型"""
    __tablename__ = 'dbc_files'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False, index=True)
    name = db.Column(db.String(500), nullable=False)
    path = db.Column(db.String(1000), nullable=False)
    signal_count = db.Column(db.Integer)
    message_count = db.Column(db.Integer)
    parsed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'signal_count': self.signal_count,
            'message_count': self.message_count,
            'parsed': self.parsed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AIHistory(db.Model):
    """AI 历史模型"""
    __tablename__ = 'ai_history'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), index=True)
    type = db.Column(db.String(50), nullable=False, index=True)  # strategy/design/testcase/script/report
    input = db.Column(db.Text)
    output = db.Column(db.Text)
    tokens_used = db.Column(db.Integer)
    model = db.Column(db.String(50))
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    duration_ms = db.Column(db.Integer)  # 执行耗时
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'type': self.type,
            'input': self.input[:500] if self.input else None,
            'output': self.output[:500] if self.output else None,
            'tokens_used': self.tokens_used,
            'model': self.model,
            'success': self.success,
            'duration_ms': self.duration_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ActivityState(db.Model):
    """测试活动状态模型
    
    跟踪每个测试活动的状态，支持test_system文档规范
    """
    __tablename__ = 'activity_states'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False, index=True)
    activity_code = db.Column(db.String(10), nullable=False, index=True)  # RA/TS/TD/TC/TScr/TE/TL/TEval/TR
    status = db.Column(db.String(50), default='not_started')  # not_started/in_progress/completed/failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    result_data = db.Column(db.Text)  # JSON结果数据
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'activity_code', name='uix_project_activity'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'activity_code': self.activity_code,
            'status': self.status,
            'progress': self.progress,
            'result_data': self.result_data,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class TestExecution(db.Model):
    """测试执行记录模型
    
    对应测试活动：TE (Test Execution)
    活动代码：ACT-TE-*
    """
    __tablename__ = 'test_executions'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey('projects.id'), nullable=False, index=True)
    test_case_id = db.Column(db.String, db.ForeignKey('test_cases.id'), index=True)
    execution_type = db.Column(db.String(50))  # HIL/SIL/Manual
    status = db.Column(db.String(50), index=True)  # running/passed/failed/blocked
    start_time = db.Column(db.DateTime, index=True)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    result_data = db.Column(db.Text)  # JSON
    error_log = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'test_case_id': self.test_case_id,
            'execution_type': self.execution_type,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
