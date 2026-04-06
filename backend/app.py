# VehicleTestAI1 - 更新后的后端 API（使用数据库）

# 首先在 app.py 开头添加数据库配置
# 在现有导入语句后添加：

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from services.ai_service import get_ai_service, GLMService

# 导入模型
from models import db, Project, Requirement, TestStrategy, TestDesign, TestCase, TestLog, DBCFile, AIHistory

app = Flask(__name__)
CORS(app)

# ===== 数据库配置 =====
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'vehicletestai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False  # 生产环境设为 False

# 初始化数据库
db.init_app(app)

# 配置
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "doc", "docx", "xlsx", "xls", "dbc", "arxml", "blf", "asc", "csv", "mf4"}

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

# 在应用上下文中创建表
with app.app_context():
    db.create_all()
    print("✅ 数据库表已初始化")

# ===== 项目管理 API =====

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """获取项目列表"""
    try:
        projects = Project.query.all()
        return jsonify({
            'success': True,
            'projects': [p.to_dict() for p in projects]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """创建项目"""
    try:
        data = request.json
        project_id = str(uuid.uuid4())
        
        project = Project(
            id=project_id,
            name=data.get('name', '未命名项目'),
            description=data.get('description', '')
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """获取项目详情"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """更新项目"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        data = request.json
        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== 需求管理 API =====

@app.route('/api/requirements/<project_id>', methods=['GET'])
def get_requirements(project_id):
    """获取需求列表"""
    try:
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        return jsonify({
            'success': True,
            'requirements': [r.to_dict() for r in requirements]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/requirements', methods=['POST'])
def create_requirement():
    """创建需求"""
    try:
        data = request.json
        req_id = str(uuid.uuid4())
        
        requirement = Requirement(
            id=req_id,
            project_id=data.get('project_id'),
            name=data.get('name', '新功能点'),
            category=data.get('category', '未分类'),
            priority=data.get('priority', 'P2'),
            description=data.get('description', ''),
            source=data.get('source', '手动添加'),
            linked_reqs=data.get('linkedReqs', '')
        )
        
        db.session.add(requirement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'requirement': requirement.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== AI 生成 API =====

@app.route('/api/ai/generate-strategy', methods=['POST'])
def generate_strategy():
    """生成测试策略"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        # 获取需求
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        req_text = '\n'.join([f"{r.id}: {r.name}\n{r.description}" for r in requirements])
        
        # 调用 AI 服务
        ai_service = get_ai_service()
        prompt = f"请根据以下需求生成测试策略：\n\n{req_text}"
        content = ai_service.generate(prompt)
        
        # 保存到数据库
        strategy_id = str(uuid.uuid4())
        strategy = TestStrategy(
            id=strategy_id,
            project_id=project_id,
            name=f"测试策略_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=content
        )
        
        db.session.add(strategy)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'strategy': strategy.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/generate-design', methods=['POST'])
def generate_design():
    """生成测试设计"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        # 获取策略
        strategies = TestStrategy.query.filter_by(project_id=project_id).all()
        strategy_text = '\n\n'.join([s.content for s in strategies])
        
        # 调用 AI 服务
        ai_service = get_ai_service()
        prompt = f"请根据以下测试策略生成测试设计：\n\n{strategy_text}"
        content = ai_service.generate(prompt)
        
        # 保存到数据库
        design_id = str(uuid.uuid4())
        design = TestDesign(
            id=design_id,
            project_id=project_id,
            name=f"测试设计_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=content
        )
        
        db.session.add(design)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'design': design.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== 测试用例 API =====

@app.route('/api/test-cases/<project_id>', methods=['GET'])
def get_test_cases(project_id):
    """获取测试用例列表"""
    try:
        test_cases = TestCase.query.filter_by(project_id=project_id).all()
        return jsonify({
            'success': True,
            'testcases': [tc.to_dict() for tc in test_cases]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== 测试策略 API =====

@app.route('/api/test-strategies/<project_id>', methods=['GET'])
def get_strategies(project_id):
    """获取测试策略列表"""
    try:
        strategies = TestStrategy.query.filter_by(project_id=project_id).all()
        return jsonify({
            'success': True,
            'strategies': [s.to_dict() for s in strategies]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== 测试设计 API =====

@app.route('/api/test-designs/<project_id>', methods=['GET'])
def get_designs(project_id):
    """获取测试设计列表"""
    try:
        designs = TestDesign.query.filter_by(project_id=project_id).all()
        return jsonify({
            'success': True,
            'designs': [d.to_dict() for d in designs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== 健康检查 =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'VehicleTestAI Backend',
        'version': '2.0.0',
        'database': 'SQLite',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
