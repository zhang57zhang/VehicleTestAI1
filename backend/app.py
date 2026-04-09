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
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入模型
from models import (
    db,
    Project,
    Requirement,
    TestStrategy,
    TestDesign,
    TestCase,
    TestLog,
    DBCFile,
    AIHistory,
)

app = Flask(__name__)
CORS(app)

# ===== AI 服务配置 =====
# 支持两种环境变量名称：GLM_API_KEY 或 ZHIPUAI_API_KEY
ZHIPUAI_API_KEY = os.environ.get("GLM_API_KEY") or os.environ.get("ZHIPUAI_API_KEY")
ZHIPUAI_MODEL = os.environ.get("GLM_MODEL") or os.environ.get(
    "ZHIPUAI_MODEL", "glm-4.7"
)


def get_configured_ai_service():
    """获取配置好的 AI 服务实例"""
    if ZHIPUAI_API_KEY:
        return get_ai_service("glm", api_key=ZHIPUAI_API_KEY, model=ZHIPUAI_MODEL)
    else:
        print("⚠️ 未配置 ZHIPUAI_API_KEY，使用 Mock 服务")
        return get_ai_service("mock")


# ===== 数据库配置 =====
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data", "vehicletestai.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False  # 生产环境设为 False

# 初始化数据库
db.init_app(app)

# 配置
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {
    "txt",
    "md",
    "pdf",
    "doc",
    "docx",
    "xlsx",
    "xls",
    "dbc",
    "arxml",
    "blf",
    "asc",
    "csv",
    "mf4",
    "py",
    "json",
}


# ===== AI配置 API =====
@app.route("/api/ai/config", methods=["GET", "OPTIONS"])
def get_ai_config():
    """获取AI配置信息"""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    return jsonify(
        {
            "success": True,
            "config": {
                "provider": "glm" if ZHIPUAI_API_KEY else "mock",
                "model": ZHIPUAI_MODEL,
                "available": bool(ZHIPUAI_API_KEY),
            },
        }
    )


@app.route("/api/ai/chat", methods=["POST", "OPTIONS"])
def ai_chat():
    """AI助手对话"""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    try:
        data = request.json
        message = data.get("message", "")
        history = data.get("history", [])

        # 获取AI服务
        ai_service = get_configured_ai_service()

        # 构建提示词
        system_prompt = "你是一个专业的车载控制器测试AI助手。你可以帮助工程师进行需求分析、测试策略制定、测试用例设计、测试脚本生成、日志分析和测试报告生成。请根据用户的问题提供专业、准确的回答，用中文回答。"

        # 构建完整提示
        full_prompt = f"{system_prompt}\n\n"

        # 添加历史对话
        if history:
            for h in history:
                role = "用户" if h.get("role") == "user" else "助手"
                full_prompt += f"{role}: {h.get('content', '')}\n"
            full_prompt += "\n"

        # 添加当前问题
        full_prompt += f"用户: {message}\n\n请回答："

        # 调用AI服务
        response = ai_service.generate(full_prompt)

        return jsonify(
            {
                "success": True,
                "response": response,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        print(f"AI Chat Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

# 在应用上下文中创建表
with app.app_context():
    db.create_all()
    print("[OK] Database tables initialized")

# ===== 项目管理 API =====


@app.route("/api/projects", methods=["GET"])
def get_projects():
    """获取项目列表"""
    try:
        projects = Project.query.all()
        return jsonify({"success": True, "projects": [p.to_dict() for p in projects]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects", methods=["POST"])
def create_project():
    """创建项目"""
    try:
        data = request.json
        project_id = str(uuid.uuid4())

        project = Project(
            id=project_id,
            name=data.get("name", "未命名项目"),
            description=data.get("description", ""),
        )

        db.session.add(project)
        db.session.commit()

        # 创建项目目录结构
        project_dir = os.path.join(UPLOAD_FOLDER, project_id)
        subdirs = [
            "requirement",
            "strategy",
            "design",
            "testcase",
            "script",
            "log",
            "evaluation",
            "report",
            "resource",
        ]
        for subdir in subdirs:
            os.makedirs(os.path.join(project_dir, subdir), exist_ok=True)
        print(f"📁 创建项目目录: {project_dir}")

        return jsonify({"success": True, "project": project.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    """获取项目详情"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404

        return jsonify({"success": True, "project": project.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects/<project_id>", methods=["PUT"])
def update_project(project_id):
    """更新项目"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404

        data = request.json
        project.name = data.get("name", project.name)
        project.description = data.get("description", project.description)

        db.session.commit()

        return jsonify({"success": True, "project": project.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    """删除项目"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404

        db.session.delete(project)
        db.session.commit()

        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects/<project_id>/sync", methods=["POST"])
def sync_project(project_id):
    """同步项目文件"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404

        # 获取项目上传目录中的文件
        upload_dir = os.path.join(UPLOAD_FOLDER, project_id)
        files = {}

        if os.path.exists(upload_dir):
            for folder in os.listdir(upload_dir):
                folder_path = os.path.join(upload_dir, folder)
                if os.path.isdir(folder_path):
                    files[folder] = []
                    for f in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, f)
                        if os.path.isfile(file_path):
                            files[folder].append(
                                {
                                    "name": f,
                                    "path": file_path,
                                    "size": os.path.getsize(file_path),
                                }
                            )

        return jsonify({"success": True, "files": files, "project": project.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 需求管理 API =====


@app.route("/api/requirements/<project_id>", methods=["GET"])
def get_requirements(project_id):
    """获取需求列表"""
    try:
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        return jsonify(
            {"success": True, "requirements": [r.to_dict() for r in requirements]}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/requirements", methods=["POST"])
def create_requirement():
    """创建需求"""
    try:
        data = request.json
        req_id = str(uuid.uuid4())

        requirement = Requirement(
            id=req_id,
            project_id=data.get("project_id"),
            name=data.get("name", "新功能点"),
            category=data.get("category", "未分类"),
            priority=data.get("priority", "P2"),
            description=data.get("description", ""),
            source=data.get("source", "手动添加"),
            linked_reqs=data.get("linkedReqs", ""),
        )

        db.session.add(requirement)
        db.session.commit()

        return jsonify({"success": True, "requirement": requirement.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/requirements/<req_id>", methods=["DELETE"])
def delete_requirement(req_id):
    """删除需求"""
    try:
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({"success": False, "error": "Requirement not found"}), 404

        db.session.delete(requirement)
        db.session.commit()

        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/requirements/<req_id>", methods=["PUT"])
def update_requirement(req_id):
    """更新需求"""
    try:
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({"success": False, "error": "Requirement not found"}), 404

        data = request.json
        requirement.name = data.get("name", requirement.name)
        requirement.description = data.get("description", requirement.description)
        requirement.category = data.get("category", requirement.category)
        requirement.priority = data.get("priority", requirement.priority)

        db.session.commit()

        return jsonify({"success": True, "requirement": requirement.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ===== AI 生成 API =====


@app.route("/api/ai/generate-strategy", methods=["POST"])
def generate_strategy():
    """生成测试策略"""
    try:
        data = request.json
        project_id = data.get("project_id")

        # 获取需求（从数据库或请求体）
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        if requirements:
            req_text = "\n".join(
                [f"{r.id}: {r.name}\n{r.description}" for r in requirements]
            )
        elif data.get("requirements"):
            # 如果请求体中提供了需求文本，直接使用
            req_text = data.get("requirements")
        else:
            # 没有需求时使用默认提示
            req_text = "请生成一个通用的 VCU 测试策略"

        # 调用 AI 服务
        ai_service = get_configured_ai_service()
        prompt = f"请根据以下需求生成测试策略：\n\n{req_text}"
        content = ai_service.generate(prompt)

        # 保存到数据库
        strategy_id = str(uuid.uuid4())
        strategy = TestStrategy(
            id=strategy_id,
            project_id=project_id,
            name=f"测试策略_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=content,
        )

        db.session.add(strategy)
        db.session.commit()

        return jsonify({"success": True, "strategy": strategy.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/generate-design", methods=["POST"])
def generate_design():
    """生成测试设计"""
    try:
        data = request.json
        project_id = data.get("project_id")

        # 获取策略
        strategies = TestStrategy.query.filter_by(project_id=project_id).all()
        strategy_text = "\n\n".join([s.content for s in strategies])

        # 调用 AI 服务
        ai_service = get_configured_ai_service()
        prompt = f"请根据以下测试策略生成测试设计：\n\n{strategy_text}"
        content = ai_service.generate(prompt)

        # 保存到数据库
        design_id = str(uuid.uuid4())
        design = TestDesign(
            id=design_id,
            project_id=project_id,
            name=f"测试设计_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=content,
        )

        db.session.add(design)
        db.session.commit()

        return jsonify({"success": True, "design": design.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 测试用例 API =====


@app.route("/api/test-cases/<project_id>", methods=["GET"])
def get_test_cases(project_id):
    """获取测试用例列表"""
    try:
        test_cases = TestCase.query.filter_by(project_id=project_id).all()
        return jsonify(
            {"success": True, "testcases": [tc.to_dict() for tc in test_cases]}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 测试策略 API =====


@app.route("/api/test-strategies/<project_id>", methods=["GET"])
def get_strategies(project_id):
    """获取测试策略列表"""
    try:
        strategies = TestStrategy.query.filter_by(project_id=project_id).all()
        return jsonify(
            {"success": True, "strategies": [s.to_dict() for s in strategies]}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/strategies/<project_id>", methods=["GET"])
def get_strategies_alias(project_id):
    """获取测试策略列表 (alias)"""
    return get_strategies(project_id)


@app.route("/api/testcases/<project_id>", methods=["GET"])
def get_testcases_alias(project_id):
    """获取测试用例列表 (alias)"""
    return get_test_cases(project_id)


# ===== 测试设计 API =====


@app.route("/api/test-designs/<project_id>", methods=["GET"])
def get_designs(project_id):
    """获取测试设计列表"""
    try:
        designs = TestDesign.query.filter_by(project_id=project_id).all()
        return jsonify({"success": True, "designs": [d.to_dict() for d in designs]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 健康检查 =====


@app.route("/api/health", methods=["GET"])
def health_check():
    """健康检查"""
    return jsonify(
        {
            "status": "healthy",
            "service": "VehicleTestAI Backend",
            "version": "2.0.0",
            "database": "SQLite",
            "timestamp": datetime.now().isoformat(),
        }
    )


# ===== 文件上传 API =====

ALLOWED_EXTENSIONS = {
    "txt",
    "md",
    "pdf",
    "doc",
    "docx",
    "xlsx",
    "xls",
    "dbc",
    "arxml",
    "blf",
    "asc",
    "csv",
    "mf4",
    "py",
    "json",
}


@app.route("/api/upload/<project_id>/<file_type>", methods=["POST"])
def upload_file(project_id, file_type):
    """上传文件"""
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        if file and allowed_file_upload(file.filename):
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())

            # 创建项目特定目录
            project_dir = os.path.join(UPLOAD_FOLDER, project_id, file_type)
            os.makedirs(project_dir, exist_ok=True)

            # 保存文件
            file_path = os.path.join(project_dir, filename)
            file.save(file_path)

            return jsonify(
                {
                    "success": True,
                    "file_id": file_id,
                    "path": file_path,
                    "filename": filename,
                }
            ), 201
        else:
            return jsonify({"success": False, "error": "File type not allowed"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def allowed_file_upload(filename):
    """检查文件扩展名"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ===== AI 生成测试用例 API =====


@app.route("/api/ai/generate-testcases", methods=["POST"])
def generate_testcases():
    """AI生成测试用例"""
    try:
        data = request.json
        project_id = data.get("project_id")
        design_content = data.get("design", "")

        # 获取设计内容
        if not design_content:
            designs = TestDesign.query.filter_by(project_id=project_id).all()
            if designs:
                design_content = designs[-1].content

        if not design_content:
            design_content = "基于VCU测试需求生成测试用例"

        # 调用 AI 服务
        ai_service = get_configured_ai_service()
        prompt = f"""请根据以下测试设计生成详细的测试用例，包括：
1. 用例ID
2. 用例名称
3. 测试目的
4. 前置条件
5. 测试步骤
6. 预期结果
7. 优先级

测试设计：
{design_content}

请生成至少10个测试用例，用表格格式输出。"""

        content = ai_service.generate(prompt)

        # 保存到数据库
        testcase_id = str(uuid.uuid4())
        testcase = TestCase(
            id=testcase_id,
            project_id=project_id,
            name=f"测试用例_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            priority="P1",
            steps=content,
            expected="参见用例内容",
        )

        db.session.add(testcase)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "testcase": {
                    "id": testcase_id,
                    "name": testcase.name,
                    "content": content,
                },
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ===== AI 生成测试脚本 API =====


@app.route("/api/ai/generate-scripts", methods=["POST"])
def generate_scripts():
    """AI生成测试脚本"""
    try:
        data = request.json
        project_id = data.get("project_id")
        testcase_content = data.get("testcases", "")

        if not testcase_content:
            testcases = TestCase.query.filter_by(project_id=project_id).all()
            if testcases:
                testcase_content = testcases[-1].steps

        # 调用 AI 服务
        ai_service = get_configured_ai_service()
        prompt = f"""请根据以下测试用例生成Python自动化测试脚本。

测试用例：
{testcase_content}

要求：
1. 使用pytest框架
2. 包含完整的测试函数
3. 支持CAN通信（使用python-can库）
4. 包含断言和错误处理

请生成完整的Python代码。"""

        content = ai_service.generate(prompt)

        return jsonify(
            {
                "success": True,
                "script": {
                    "language": "python",
                    "framework": "pytest",
                    "content": content,
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===== AI 解析日志 API =====


@app.route("/api/ai/parse-log", methods=["POST"])
def parse_log():
    """AI解析测试日志"""
    try:
        data = request.json
        project_id = data.get("project_id")
        log_content = data.get("log_content", "")

        if not log_content:
            log_content = "模拟日志：测试执行完成，50个用例通过，2个失败"

        # 调用 AI 服务
        ai_service = get_configured_ai_service()
        prompt = f"""请分析以下测试日志，提取关键信息：

日志内容：
{log_content}

请输出：
1. 测试摘要（通过/失败数量）
2. 发现的问题
3. 性能数据
4. 建议的改进措施"""

        content = ai_service.generate(prompt)

        # Save to database
        log_id = str(uuid.uuid4())
        log = TestLog(
            id=log_id,
            project_id=project_id,
            signal="log_analysis",
            value=content[:500] if content else "",
            unit="text",
            timestamp=datetime.now().isoformat(),
        )

        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "analysis": {
                    "id": log_id,
                    "summary": content[:500] if content else "",
                    "full_result": content,
                },
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ===== AI 生成测试报告 API =====


@app.route("/api/ai/generate-report", methods=["POST"])
def generate_report():
    """AI生成测试报告"""
    try:
        data = request.json
        project_id = data.get("project_id")

        # 收集项目数据
        project = Project.query.get(project_id)
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        strategies = TestStrategy.query.filter_by(project_id=project_id).all()
        designs = TestDesign.query.filter_by(project_id=project_id).all()
        testcases = TestCase.query.filter_by(project_id=project_id).all()
        logs = TestLog.query.filter_by(project_id=project_id).all()

        # 构建报告数据
        report_data = f"""
项目：{project.name if project else "未知"}
需求数量：{len(requirements)}
测试策略数量：{len(strategies)}
测试设计数量：{len(designs)}
测试用例数量：{len(testcases)}
测试日志数量：{len(logs)}
"""

        # 调用 AI 服务
        ai_service = get_configured_ai_service()
        prompt = f"""请根据以下测试数据生成一份完整的测试报告：

{report_data}

要求包含：
1. 测试概述
2. 测试范围
3. 测试结果统计
4. 问题清单
5. 风险评估
6. 结论与建议

请使用Markdown格式输出。"""

        content = ai_service.generate(prompt)

        return jsonify(
            {
                "success": True,
                "report": {
                    "project_name": project.name if project else "未知",
                    "generated_at": datetime.now().isoformat(),
                    "content": content,
                    "statistics": {
                        "requirements": len(requirements),
                        "strategies": len(strategies),
                        "designs": len(designs),
                        "testcases": len(testcases),
                        "logs": len(logs),
                    },
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===== DBC 解析 API =====


@app.route("/api/dbc/parse", methods=["POST"])
def parse_dbc():
    """解析DBC文件"""
    try:
        data = request.json
        dbc_content = data.get("content", "")

        # 简单解析DBC
        messages = []
        signals = []

        if dbc_content:
            # 解析BO_（报文）
            for line in dbc_content.split("\n"):
                if line.startswith("BO_"):
                    parts = line.split()
                    if len(parts) >= 3:
                        messages.append(
                            {
                                "id": parts[1],
                                "name": parts[2],
                                "dlc": parts[3] if len(parts) > 3 else 8,
                            }
                        )
                # 解析SG_（信号）
                elif line.strip().startswith("SG_"):
                    parts = line.split()
                    if len(parts) >= 2:
                        signals.append(
                            {
                                "name": parts[1],
                                "start_bit": parts[3] if len(parts) > 3 else 0,
                                "length": parts[4] if len(parts) > 4 else 8,
                            }
                        )

        return jsonify(
            {
                "success": True,
                "dbc": {
                    "messages": messages[:20],  # 限制返回数量
                    "signals": signals[:50],
                    "message_count": len(messages),
                    "signal_count": len(signals),
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 获取DBC列表 API =====


@app.route("/api/dbc/list/<project_id>", methods=["GET"])
def list_dbc(project_id):
    """获取项目的DBC文件列表"""
    try:
        dbc_dir = os.path.join(UPLOAD_FOLDER, project_id, "dbcFile")
        if os.path.exists(dbc_dir):
            files = os.listdir(dbc_dir)
            dbc_files = [f for f in files if f.endswith(".dbc")]
            return jsonify({"success": True, "files": dbc_files})
        return jsonify({"success": True, "files": []})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/parse-requirements", methods=["POST"])
def parse_requirements():
    """AI解析需求文档"""
    try:
        data = request.json
        project_id = data.get("project_id")
        content = data.get("content", "")
        file_id = data.get("file_id")

        # 如果提供了文件ID，读取文件内容
        if file_id and project_id:
            # 查找项目上传目录中的需求文件
            req_dir = os.path.join(UPLOAD_FOLDER, project_id, "requirement")
            if os.path.exists(req_dir):
                files = os.listdir(req_dir)
                if files:
                    # 读取第一个文件
                    file_path = os.path.join(req_dir, files[0])
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    print(f"📄 读取需求文件: {file_path}, 大小: {len(content)} 字符")

        # 如果提供了文档内容，直接解析
        if content:
            ai_service = get_configured_ai_service()
            prompt = f"""分析以下需求文档，提取所有功能点。

需求文档：
{content[:4000]}

请严格按照以下JSON格式返回，不要添加任何其他内容：
{{
  "functional_requirements": [
    {{
      "name": "功能点名称",
      "description": "功能点详细描述",
      "category": "功能需求/性能需求/安全需求",
      "priority": "P0/P1/P2/P3"
    }}
  ]
}}
"""
            result = ai_service.generate(prompt)

            # 尝试解析JSON
            analysis = {"raw_content": result, "functional_requirements": []}
            try:
                # 尝试提取JSON部分
                import re

                json_match = re.search(r"\{[\s\S]*\}", result)
                if json_match:
                    parsed = json.loads(json_match.group())
                    if "functional_requirements" in parsed:
                        # 为每个功能点添加ID
                        for i, req in enumerate(parsed["functional_requirements"]):
                            if "id" not in req:
                                req["id"] = f"FP_{i + 1:03d}"
                        analysis = parsed

                        # 保存功能点到数据库和文件
                        if project_id:
                            for req_data in parsed["functional_requirements"]:
                                existing = Requirement.query.filter_by(
                                    project_id=project_id, name=req_data.get("name")
                                ).first()
                                if not existing:
                                    requirement = Requirement(
                                        id=str(uuid.uuid4()),
                                        project_id=project_id,
                                        name=req_data.get("name", "未命名"),
                                        description=req_data.get("description", ""),
                                        category=req_data.get("category", "未分类"),
                                        priority=req_data.get("priority", "P2"),
                                        source="AI解析",
                                    )
                                    db.session.add(requirement)
                            db.session.commit()

                            # 保存到文件
                            req_file_dir = os.path.join(
                                UPLOAD_FOLDER, project_id, "requirement"
                            )
                            os.makedirs(req_file_dir, exist_ok=True)
                            req_file_path = os.path.join(
                                req_file_dir, "requirements_parsed.json"
                            )
                            with open(req_file_path, "w", encoding="utf-8") as f:
                                json.dump(
                                    parsed["functional_requirements"],
                                    f,
                                    ensure_ascii=False,
                                    indent=2,
                                )
                            print(f"✅ 已保存功能点到: {req_file_path}")
            except Exception as e:
                print(f"JSON parse error: {e}")

            return jsonify({"success": True, "analysis": analysis})

        # 否则从数据库读取
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        if not requirements:
            return jsonify(
                {"success": False, "error": "没有找到需求，请先上传需求文档"}
            ), 200
        req_text = "\n".join([f"- {r.name}: {r.description}" for r in requirements])
        ai_service = get_configured_ai_service()
        result = ai_service.generate(f"请分析以下需求：\n{req_text}")
        return jsonify({"success": True, "analysis": {"raw_content": result}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/review-requirements", methods=["POST"])
def review_requirements():
    """AI审核需求"""
    try:
        data = request.json
        project_id = data.get("project_id")
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        if not requirements:
            return jsonify({"success": False, "error": "没有找到需求"}), 200
        req_text = "\n".join([f"- {r.name}: {r.description}" for r in requirements])
        ai_service = get_configured_ai_service()
        content = ai_service.generate(f"请审核以下需求：\n{req_text}")
        return jsonify({"success": True, "review": {"content": content, "score": 85}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/testcases", methods=["POST"])
def add_testcase():
    """手动添加测试用例"""
    try:
        data = request.json
        testcase = TestCase(
            id=str(uuid.uuid4()),
            project_id=data.get("project_id"),
            name=data.get("name", "未命名"),
            priority=data.get("priority", "P2"),
            steps=data.get("description", ""),
            expected=data.get("expected", ""),
        )
        db.session.add(testcase)
        db.session.commit()
        return jsonify({"success": True, "testcase": testcase.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/test-results/<project_id>", methods=["GET"])
def get_test_results(project_id):
    """读取测试结果"""
    try:
        logs = TestLog.query.filter_by(project_id=project_id).all()
        results = [
            {"id": l.id, "name": l.signal or "Unknown", "value": l.value} for l in logs
        ]
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/execution-status/<project_id>", methods=["GET"])
def get_execution_status(project_id):
    """读取执行情况"""
    try:
        return jsonify(
            {
                "success": True,
                "status": {
                    "requirements": Requirement.query.filter_by(
                        project_id=project_id
                    ).count(),
                    "strategies": TestStrategy.query.filter_by(
                        project_id=project_id
                    ).count(),
                    "designs": TestDesign.query.filter_by(
                        project_id=project_id
                    ).count(),
                    "testcases": TestCase.query.filter_by(
                        project_id=project_id
                    ).count(),
                    "progress": 75,
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dts/<project_id>", methods=["GET"])
def get_dts(project_id):
    """读取缺陷DTS"""
    try:
        logs = TestLog.query.filter_by(project_id=project_id).all()
        defects = [
            {"id": l.id, "name": l.signal or "Unknown", "severity": "medium"}
            for l in logs
        ]
        return jsonify({"success": True, "defects": defects})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/match-testcases", methods=["POST"])
def match_testcases():
    """测试用例匹配"""
    try:
        data = request.json
        project_id = data.get("project_id")
        testcases = TestCase.query.filter_by(project_id=project_id).all()
        matches = [{"testcase_id": tc.id, "testcase_name": tc.name} for tc in testcases]
        return jsonify({"success": True, "matches": matches})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/generate-dts", methods=["POST"])
def generate_dts():
    """生成DTS"""
    try:
        data = request.json
        project_id = data.get("project_id")
        ai_service = get_configured_ai_service()
        content = ai_service.generate(f"请为项目{project_id}生成缺陷追踪表")
        return jsonify({"success": True, "dts": content})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/export/analysis/<project_id>", methods=["GET"])
def export_analysis(project_id):
    """导出分析结果"""
    try:
        return jsonify(
            {
                "success": True,
                "export": {
                    "project_id": project_id,
                    "requirements": Requirement.query.filter_by(
                        project_id=project_id
                    ).count(),
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/generate-evaluation", methods=["POST"])
def generate_evaluation():
    """生成测试评估"""
    try:
        data = request.json
        project_id = data.get("project_id")
        ai_service = get_configured_ai_service()
        content = ai_service.generate(f"请为项目{project_id}生成测试评估")
        return jsonify({"success": True, "evaluation": {"content": content}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 测试脚本扩展API =====


@app.route("/api/automation/config", methods=["POST"])
def automation_config():
    """执行目录配置"""
    try:
        data = request.json
        return jsonify(
            {"success": True, "config": {"project_id": data.get("project_id")}}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/upload/<project_id>/scriptTemplate", methods=["POST"])
def upload_script_template(project_id):
    """上传脚本模板"""
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "没有文件"}), 400
        file = request.files["file"]
        upload_dir = os.path.join(UPLOAD_FOLDER, project_id, "scriptTemplate")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, secure_filename(file.filename))
        file.save(filepath)
        return jsonify({"success": True, "filename": file.filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
