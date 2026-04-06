# -*- coding: utf-8 -*-
"""
车载控制器测试AI平台 - Flask后端服务
提供AI生成、项目管理、文件处理等REST API接口
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from services.ai_service import get_ai_service, GLMService

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = "uploads"
PROJECTS_FILE = "data/projects.json"
AI_CONFIG_FILE = "data/ai_config.json"
AI_STATS_FILE = "data/ai_stats.json"
ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "doc", "docx", "xlsx", "xls"}

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)


# ==================== AI统计系统 ====================


def load_ai_stats():
    """加载AI使用统计数据"""
    if os.path.exists(AI_STATS_FILE):
        with open(AI_STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "total_calls": 0,
        "total_hours_saved": 0.0,
        "total_tokens_used": 0,
        "skill_usage": {
            "需求分析": {"count": 0, "last_used": None},
            "策略生成": {"count": 0, "last_used": None},
            "测试设计": {"count": 0, "last_used": None},
            "用例生成": {"count": 0, "last_used": None},
            "脚本生成": {"count": 0, "last_used": None},
            "报告生成": {"count": 0, "last_used": None},
            "日志分析": {"count": 0, "last_used": None},
            "评估生成": {"count": 0, "last_used": None},
            "报告审查": {"count": 0, "last_used": None},
            "脚本优化": {"count": 0, "last_used": None},
        },
        "history": [],
        "monthly_stats": {},
        "adoption_rate": 100.0,
    }


def save_ai_stats(stats):
    """保存AI使用统计数据"""
    with open(AI_STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_ai_usage(
    skill_type, content_summary, status, duration, tokens_used=0, project_id=None
):
    """记录AI使用情况

    Args:
        skill_type: 技能类型 (需求分析, 策略生成, 等)
        content_summary: 请求内容摘要
        status: 状态 (成功, 失败, 待优化)
        duration: 耗时(秒)
        tokens_used: 使用的token数
        project_id: 项目ID
    """
    stats = load_ai_stats()

    # 更新总调用次数
    stats["total_calls"] += 1

    # 计算节省工时 (假设每次AI调用平均节省0.1小时)
    hours_saved = 0.1
    stats["total_hours_saved"] += hours_saved

    # 更新token使用量
    stats["total_tokens_used"] += tokens_used

    # 更新技能使用统计
    if skill_type in stats["skill_usage"]:
        stats["skill_usage"][skill_type]["count"] += 1
        stats["skill_usage"][skill_type]["last_used"] = datetime.now().isoformat()

    # 添加历史记录 (保留最近100条)
    history_entry = {
        "id": str(uuid.uuid4()),
        "time": datetime.now().isoformat(),
        "type": skill_type,
        "content": content_summary[:100]
        if len(content_summary) > 100
        else content_summary,
        "status": status,
        "duration": f"{duration:.1f}s",
        "duration_seconds": duration,
        "tokens": tokens_used,
        "project_id": project_id,
    }
    stats["history"].insert(0, history_entry)
    stats["history"] = stats["history"][:100]  # 只保留最近100条

    # 更新月度统计
    month_key = datetime.now().strftime("%Y-%m")
    if month_key not in stats["monthly_stats"]:
        stats["monthly_stats"][month_key] = {
            "calls": 0,
            "hours_saved": 0.0,
            "by_skill": {},
        }
    stats["monthly_stats"][month_key]["calls"] += 1
    stats["monthly_stats"][month_key]["hours_saved"] += hours_saved

    if skill_type not in stats["monthly_stats"][month_key]["by_skill"]:
        stats["monthly_stats"][month_key]["by_skill"][skill_type] = 0
    stats["monthly_stats"][month_key]["by_skill"][skill_type] += 1

    save_ai_stats(stats)
    return stats


# 全局AI配置
def load_ai_config():
    """加载AI配置"""
    if os.path.exists(AI_CONFIG_FILE):
        with open(AI_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "provider": "glm",
        "model": "glm-4-plus",
        "api_key": "",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "max_tokens": 4096,
        "temperature": 0.7,
    }


def save_ai_config(config):
    """保存AI配置"""
    with open(AI_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_ai_service_from_config():
    """根据配置获取AI服务实例"""
    config = load_ai_config()
    return get_ai_service(
        service_type=config.get("provider", "glm"),
        api_key=config.get("api_key"),
        model=config.get("model"),
    )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_projects():
    """加载项目数据"""
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_projects(projects):
    """保存项目数据"""
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


# ==================== AI统计API ====================


@app.route("/api/ai/stats", methods=["GET"])
def get_ai_stats():
    """获取AI使用统计数据"""
    stats = load_ai_stats()

    # 计算活跃技能数
    active_skills = sum(1 for s in stats["skill_usage"].values() if s["count"] > 0)

    # 获取本月统计
    month_key = datetime.now().strftime("%Y-%m")
    monthly = stats["monthly_stats"].get(month_key, {"calls": 0, "hours_saved": 0.0})

    return jsonify(
        {
            "success": True,
            "stats": {
                "total_calls": stats["total_calls"],
                "hours_saved": round(monthly["hours_saved"], 1),
                "total_hours_saved": round(stats["total_hours_saved"], 1),
                "adoption_rate": stats["adoption_rate"],
                "active_skills": active_skills,
                "total_tokens": stats["total_tokens_used"],
            },
            "skill_usage": stats["skill_usage"],
            "history": stats["history"][:20],  # 返回最近20条
            "monthly_stats": stats["monthly_stats"],
        }
    )


@app.route("/api/ai/stats/reset", methods=["POST"])
def reset_ai_stats():
    """重置AI统计数据"""
    stats = {
        "total_calls": 0,
        "total_hours_saved": 0.0,
        "total_tokens_used": 0,
        "skill_usage": {
            "需求分析": {"count": 0, "last_used": None},
            "策略生成": {"count": 0, "last_used": None},
            "测试设计": {"count": 0, "last_used": None},
            "用例生成": {"count": 0, "last_used": None},
            "脚本生成": {"count": 0, "last_used": None},
            "报告生成": {"count": 0, "last_used": None},
            "日志分析": {"count": 0, "last_used": None},
            "评估生成": {"count": 0, "last_used": None},
            "报告审查": {"count": 0, "last_used": None},
            "脚本优化": {"count": 0, "last_used": None},
        },
        "history": [],
        "monthly_stats": {},
        "adoption_rate": 100.0,
    }
    save_ai_stats(stats)
    return jsonify({"success": True, "message": "统计数据已重置"})


# ==================== 项目管理API ====================


def sync_project_files_with_disk(project_id):
    """同步项目文件记录与磁盘文件"""
    projects = load_projects()
    if project_id not in projects:
        return None, "项目不存在"

    project = projects[project_id]
    project_path = project.get(
        "path", os.path.join("projects", project.get("name", project_id))
    )

    # 定义要同步的文件夹
    folders = [
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

    synced_files = {}

    for folder in folders:
        folder_path = os.path.join(project_path, folder)
        synced_files[folder] = {}

        if os.path.exists(folder_path):
            # 扫描磁盘上的文件
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    try:
                        file_stat = os.stat(file_path)
                        synced_files[folder][filename] = {
                            "name": filename,
                            "path": file_path,
                            "size": file_stat.st_size,
                            "created": datetime.fromtimestamp(
                                file_stat.st_ctime
                            ).isoformat(),
                            "modified": datetime.fromtimestamp(
                                file_stat.st_mtime
                            ).isoformat(),
                        }
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")

    # 更新项目文件记录
    project["files"] = synced_files

    # 从最新的testcase JSON文件加载测试用例
    testcase_folder = os.path.join(project_path, "testcase")
    if os.path.exists(testcase_folder):
        testcase_files = [f for f in os.listdir(testcase_folder) if f.endswith(".json")]
        if testcase_files:
            # 按修改时间排序，获取最新的文件
            testcase_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(testcase_folder, f)),
                reverse=True,
            )
            latest_file = os.path.join(testcase_folder, testcase_files[0])
            try:
                with open(latest_file, "r", encoding="utf-8") as f:
                    testcases = json.load(f)
                    if isinstance(testcases, list):
                        project["testcases"] = testcases
                        print(
                            f"Loaded {len(testcases)} testcases from {testcase_files[0]}"
                        )
            except Exception as e:
                print(f"Error loading testcases from {latest_file}: {e}")

    # 从script文件夹加载脚本文件
    script_folder = os.path.join(project_path, "script")
    if os.path.exists(script_folder):
        scripts = []
        for filename in os.listdir(script_folder):
            if filename.endswith((".py", ".robot", ".c", ".cpp", ".m")):
                file_path = os.path.join(script_folder, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    # Determine language from extension
                    ext = os.path.splitext(filename)[1]
                    lang_map = {
                        ".py": "Python",
                        ".robot": "Robot",
                        ".c": "C",
                        ".cpp": "C++",
                        ".m": "MATLAB",
                    }
                    scripts.append(
                        {
                            "id": "SCR_" + filename.replace(".", "_"),
                            "name": filename,
                            "language": lang_map.get(ext, "Unknown"),
                            "framework": "pytest" if ext == ".py" else "native",
                            "content": content,
                        }
                    )
                except Exception as e:
                    print(f"Error loading script {file_path}: {e}")
        if scripts:
            # Merge with existing scripts (preserve any additional metadata)
            existing_ids = {s.get("id") for s in project.get("scripts", [])}
            for script in scripts:
                if script["id"] not in existing_ids:
                    project.setdefault("scripts", []).append(script)
            print(f"Loaded {len(scripts)} scripts from disk")

    project["updated"] = datetime.now().isoformat()
    save_projects(projects)

    return synced_files, None


@app.route("/api/projects/<project_id>/sync", methods=["POST"])
def sync_project_files(project_id):
    """同步项目文件记录与磁盘文件"""
    synced_files, error = sync_project_files_with_disk(project_id)

    if error:
        return jsonify({"success": False, "error": error}), 404

    return jsonify({"success": True, "message": "文件同步完成", "files": synced_files})


@app.route("/api/projects", methods=["GET"])
def get_projects():
    """获取所有项目列表"""
    projects = load_projects()
    project_list = []
    for pid, p in projects.items():
        project_list.append(
            {
                "id": pid,
                "name": p.get("name", ""),
                "created": p.get("created", ""),
                "updated": p.get("updated", ""),
            }
        )
    return jsonify({"success": True, "projects": project_list})


@app.route("/api/projects", methods=["POST"])
def create_project():
    """创建新项目"""
    data = request.json
    name = data.get("name", "未命名项目")
    custom_path = data.get("path", None)  # Custom path from user
    project_id = str(uuid.uuid4())

    projects = load_projects()
    projects[project_id] = {
        "id": project_id,
        "name": name,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "files": {},
        "settings": {},
        "requirements": None,
        "strategy": None,
        "designs": [],
        "testcases": [],
        "scripts": [],
        "logs": [],
        "evaluation": None,
        "report": None,
        "resources": {"benches": [], "personnel": []},
    }
    save_projects(projects)

    # Create project folder structure on disk
    if custom_path:
        # Use custom path if provided
        project_dir = os.path.join(custom_path, name)
    else:
        # Use default path
        project_dir = os.path.join("projects", name)

    subfolders = [
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
    try:
        os.makedirs(project_dir, exist_ok=True)
        for subfolder in subfolders:
            os.makedirs(os.path.join(project_dir, subfolder), exist_ok=True)
        # Store the actual path in project data
        projects[project_id]["path"] = os.path.abspath(project_dir)
        save_projects(projects)
    except Exception as e:
        print(f"Warning: Could not create project folders: {e}")
        project_dir = "projects/" + name

    return jsonify(
        {"success": True, "project_id": project_id, "name": name, "path": project_dir}
    )


@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    """获取项目详情"""
    projects = load_projects()
    if project_id not in projects:
        return jsonify({"success": False, "error": "项目不存在"}), 404
    return jsonify({"success": True, "project": projects[project_id]})


@app.route("/api/projects/<project_id>", methods=["PUT"])
def update_project(project_id):
    """更新项目"""
    data = request.json
    projects = load_projects()
    if project_id not in projects:
        return jsonify({"success": False, "error": "项目不存在"}), 404

    projects[project_id].update(data)
    projects[project_id]["updated"] = datetime.now().isoformat()
    save_projects(projects)

    return jsonify({"success": True})


@app.route("/api/projects/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    """删除项目"""
    projects = load_projects()
    if project_id in projects:
        del projects[project_id]
        save_projects(projects)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "项目不存在"}), 404


# ==================== 文件保存API ====================


@app.route("/api/save-file/<project_id>/<folder>", methods=["POST"])
def save_file_to_disk(project_id, folder):
    """保存文件到磁盘"""
    data = request.json
    filename = data.get("filename", "untitled.md")
    content = data.get("content", "")

    projects = load_projects()
    if project_id not in projects:
        return jsonify({"success": False, "error": "项目不存在"}), 404

    project = projects[project_id]
    project_path = project.get(
        "path", os.path.join("projects", project.get("name", project_id))
    )

    # Determine the full file path
    file_path = os.path.join(project_path, folder, filename)

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write file to disk
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Update project files record
        if "files" not in project:
            project["files"] = {}
        if folder not in project["files"]:
            project["files"][folder] = {}

        project["files"][folder][filename] = {
            "name": filename,
            "path": file_path,
            "size": len(content),
            "created": datetime.now().isoformat(),
        }

        project["updated"] = datetime.now().isoformat()
        save_projects(projects)

        return jsonify({"success": True, "message": "文件保存成功", "path": file_path})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== 文件上传API ====================


@app.route("/api/upload/<project_id>/<file_type>", methods=["POST"])
def upload_file(project_id, file_type):
    """上传文件到项目"""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "没有文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "没有选择文件"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        ext = filename.rsplit(".", 1)[1].lower()
        stored_filename = f"{file_id}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, stored_filename)
        file.save(filepath)

        # 更新项目数据
        projects = load_projects()
        if project_id not in projects:
            return jsonify({"success": False, "error": "项目不存在"}), 404

        # 读取文件内容
        content = ""
        if ext in ["txt", "md"]:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        projects[project_id]["files"][file_id] = {
            "id": file_id,
            "name": filename,
            "type": file_type,
            "ext": ext,
            "path": stored_filename,
            "content": content,
            "uploaded": datetime.now().isoformat(),
        }
        projects[project_id]["updated"] = datetime.now().isoformat()
        save_projects(projects)

        return jsonify(
            {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "content": content,
            }
        )

    return jsonify({"success": False, "error": "不支持的文件类型"}), 400


@app.route("/api/files/<project_id>/<file_id>", methods=["DELETE"])
def delete_file(project_id, file_id):
    """删除项目文件"""
    projects = load_projects()
    if project_id in projects and file_id in projects[project_id]["files"]:
        filepath = os.path.join(
            UPLOAD_FOLDER, projects[project_id]["files"][file_id]["path"]
        )
        if os.path.exists(filepath):
            os.remove(filepath)
        del projects[project_id]["files"][file_id]
        projects[project_id]["updated"] = datetime.now().isoformat()
        save_projects(projects)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "文件不存在"}), 404


# ==================== AI生成API ====================


def save_ai_content_to_disk(project_id, folder, filename, content):
    """保存AI生成的内容到磁盘文件并更新项目文件记录"""
    projects = load_projects()
    if project_id not in projects:
        return False, "项目不存在"

    project = projects[project_id]
    project_path = project.get(
        "path", os.path.join("projects", project.get("name", project_id))
    )

    # 构建完整文件路径
    folder_path = os.path.join(project_path, folder)
    file_path = os.path.join(folder_path, filename)

    try:
        # 确保目录存在
        os.makedirs(folder_path, exist_ok=True)

        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # 更新项目文件记录
        if "files" not in project:
            project["files"] = {}
        if folder not in project["files"]:
            project["files"][folder] = {}

        project["files"][folder][filename] = {
            "name": filename,
            "path": file_path,
            "size": len(content),
            "created": datetime.now().isoformat(),
        }

        save_projects(projects)
        return True, file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return False, str(e)


@app.route("/api/ai/generate-strategy", methods=["POST"])
def generate_strategy():
    """
    生成测试策略
    请求体: {
        "project_id": "项目ID",
        "requirements": "需求内容",
        "system_design": "系统设计内容",
        "skills": ["技能1", "技能2"],
        "engineer_requirements": "工程师要求"
    }
    """
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    # 获取需求和系统设计内容
    requirements = data.get("requirements", "")
    system_design = data.get("system_design", "")
    skills = data.get("skills", [])
    engineer_req = data.get("engineer_requirements", "")

    try:
        # 调用AI服务生成策略
        strategy = generate_test_strategy_ai(
            requirements, system_design, skills, engineer_req
        )

        # 计算耗时
        duration = (datetime.now() - start_time).total_seconds()

        # 记录AI使用
        record_ai_usage(
            skill_type="策略生成",
            content_summary=f"生成测试策略 - {requirements[:50] if requirements else '需求分析'}",
            status="成功",
            duration=duration,
            tokens_used=len(strategy) if strategy else 0,
            project_id=project_id,
        )

        # 保存到项目
        projects = load_projects()
        if project_id in projects:
            projects[project_id]["strategy"] = {
                "content": strategy,
                "generated": datetime.now().isoformat(),
                "skills": skills,
                "requirements": engineer_req,
            }
            projects[project_id]["updated"] = datetime.now().isoformat()
            save_projects(projects)

            # 保存到磁盘文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"strategy_{timestamp}.md"
            save_ai_content_to_disk(project_id, "strategy", filename, strategy)

        return jsonify({"success": True, "strategy": strategy})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            skill_type="策略生成",
            content_summary=f"生成测试策略失败",
            status="失败",
            duration=duration,
            project_id=project_id,
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/generate-design", methods=["POST"])
def generate_design():
    """生成测试设计"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    requirements = data.get("requirements", "")

    try:
        designs = generate_test_design_ai(requirements)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="测试设计",
            content_summary=f"生成测试设计",
            status="成功",
            duration=duration,
            tokens_used=len(str(designs)),
            project_id=project_id,
        )

        projects = load_projects()
        if project_id in projects:
            projects[project_id]["designs"] = designs
            projects[project_id]["updated"] = datetime.now().isoformat()
            save_projects(projects)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if isinstance(designs, list) and len(designs) > 0:
                design_content = (
                    "\n\n---\n\n".join(designs)
                    if isinstance(designs[0], str)
                    else json.dumps(designs, ensure_ascii=False, indent=2)
                )
            else:
                design_content = str(designs)
            filename = f"design_{timestamp}.md"
            save_ai_content_to_disk(project_id, "design", filename, design_content)

        return jsonify({"success": True, "designs": designs})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "测试设计", "生成测试设计失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/generate-testcases", methods=["POST"])
def generate_testcases():
    """生成测试用例"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    requirements = data.get("requirements", "")
    designs = data.get("designs", [])

    try:
        testcases = generate_testcases_ai(requirements, designs)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="用例生成",
            content_summary=f"生成测试用例",
            status="成功",
            duration=duration,
            tokens_used=len(str(testcases)),
            project_id=project_id,
        )

        projects = load_projects()
        if project_id in projects:
            projects[project_id]["testcases"] = testcases
            projects[project_id]["updated"] = datetime.now().isoformat()
            save_projects(projects)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if isinstance(testcases, list):
                testcase_content = json.dumps(testcases, ensure_ascii=False, indent=2)
            else:
                testcase_content = str(testcases)
            filename = f"testcases_{timestamp}.json"
        save_ai_content_to_disk(project_id, "testcase", filename, testcase_content)

        return jsonify({"success": True, "testcases": testcases})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "用例生成", "生成测试用例失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/generate-scripts", methods=["POST"])
def generate_scripts():
    """生成测试脚本"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    testcases = data.get("testcases", [])
    framework = data.get("framework", "pytest")

    try:
        scripts = generate_scripts_ai(testcases, framework)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="脚本生成",
            content_summary=f"生成{framework}测试脚本",
            status="成功",
            duration=duration,
            tokens_used=len(str(scripts)),
            project_id=project_id,
        )

        projects = load_projects()
        if project_id in projects:
            projects[project_id]["scripts"] = scripts
            projects[project_id]["updated"] = datetime.now().isoformat()
            save_projects(projects)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if isinstance(scripts, list) and len(scripts) > 0:
                for i, script in enumerate(scripts):
                    if isinstance(script, dict):
                        script_content = script.get("content", str(script))
                        script_name = script.get("name", f"script_{i + 1}.py")
                    else:
                        script_content = str(script)
                        script_name = f"script_{timestamp}_{i + 1}.py"
                    save_ai_content_to_disk(
                        project_id, "script", script_name, script_content
                    )
            else:
                filename = f"script_{timestamp}.py"
                save_ai_content_to_disk(project_id, "script", filename, str(scripts))

        return jsonify({"success": True, "scripts": scripts})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "脚本生成", "生成测试脚本失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/parse-log", methods=["POST"])
def parse_log():
    """解析测试日志"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    log_content = data.get("log_content", "")

    try:
        parsed = parse_log_ai(log_content)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="日志分析",
            content_summary=f"解析测试日志",
            status="成功",
            duration=duration,
            tokens_used=len(str(parsed)),
            project_id=project_id,
        )

        projects = load_projects()
        if project_id in projects:
            projects[project_id]["logs"].append(
                {
                    "content": log_content,
                    "parsed": parsed,
                    "parsed_at": datetime.now().isoformat(),
                }
            )
            projects[project_id]["updated"] = datetime.now().isoformat()
            save_projects(projects)

        return jsonify({"success": True, "parsed": parsed})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "日志分析", "解析测试日志失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/generate-evaluation", methods=["POST"])
def generate_evaluation():
    """生成测试评估"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    test_results = data.get("test_results", {})
    metrics = data.get("metrics", {})

    try:
        evaluation = generate_evaluation_ai(test_results, metrics)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="评估生成",
            content_summary=f"生成测试评估",
            status="成功",
            duration=duration,
            tokens_used=len(str(evaluation)),
            project_id=project_id,
        )

        projects = load_projects()
        if project_id in projects:
            projects[project_id]["evaluation"] = {
                "content": evaluation,
                "test_results": test_results,
                "metrics": metrics,
                "generated": datetime.now().isoformat(),
            }
            projects[project_id]["updated"] = datetime.now().isoformat()
            save_projects(projects)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_{timestamp}.md"
            save_ai_content_to_disk(project_id, "evaluation", filename, evaluation)

        return jsonify({"success": True, "evaluation": evaluation})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "评估生成", "生成测试评估失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/generate-report", methods=["POST"])
def generate_report():
    """生成测试报告"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    report_type = data.get("report_type", "综合报告")

    try:
        report = generate_report_ai(project_id, report_type)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="报告生成",
            content_summary=f"生成{report_type}",
            status="成功",
            duration=duration,
            tokens_used=len(str(report)),
            project_id=project_id,
        )

        projects = load_projects()
        if project_id in projects:
            projects[project_id]["report"] = {
                "content": report,
                "type": report_type,
                "generated": datetime.now().isoformat(),
            }
            projects[project_id]["updated"] = datetime.now().isoformat()
            save_projects(projects)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.md"
            save_ai_content_to_disk(project_id, "report", filename, report)

        return jsonify({"success": True, "report": report})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "报告生成", "生成测试报告失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/analyze-requirements", methods=["POST"])
def analyze_requirements():
    """分析需求文档"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    content = data.get("content", "")

    try:
        analysis = analyze_requirements_ai(content)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="需求分析",
            content_summary=f"分析需求文档",
            status="成功",
            duration=duration,
            tokens_used=len(str(analysis)),
            project_id=project_id,
        )

        projects = load_projects()
        if project_id in projects:
            projects[project_id]["requirements"] = {
                "content": content,
                "analysis": analysis,
                "analyzed": datetime.now().isoformat(),
            }
            projects[project_id]["updated"] = datetime.now().isoformat()
            save_projects(projects)

        return jsonify({"success": True, "analysis": analysis})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "需求分析", "分析需求文档失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/review-report", methods=["POST"])
def review_report():
    """AI审查测试报告"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")
    report_content = data.get("report_content", "")

    try:
        review = review_report_ai(report_content)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="报告审查",
            content_summary=f"审查测试报告",
            status="成功",
            duration=duration,
            tokens_used=len(str(review)),
            project_id=project_id,
        )

        return jsonify({"success": True, "review": review})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "报告审查", "审查测试报告失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/optimize-script", methods=["POST"])
def optimize_script():
    """优化测试脚本"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    script_content = data.get("script_content", "")

    try:
        optimized = optimize_script_ai(script_content)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="脚本优化",
            content_summary=f"优化测试脚本",
            status="成功",
            duration=duration,
            tokens_used=len(str(optimized)),
            project_id=project_id,
        )

        return jsonify({"success": True, "optimized": optimized})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "脚本优化", "优化测试脚本失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/review-requirements", methods=["POST"])
def review_requirements():
    """AI审核需求文档"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")
    file_name = data.get("file_name", "未知文件")
    file_content = data.get("file_content", "")
    function_points = data.get("function_points", [])

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    try:
        ai_service = get_ai_service_from_config()

        prompt = f"""你是一个专业的车载控制器测试工程师，请对以下需求文档进行全面审核。

需求文件名称: {file_name}

需求文档内容:
{file_content[:3000]}

已识别的功能点:
{json.dumps([{"id": p.get("id"), "name": p.get("name"), "description": p.get("description", "")[:100]} for p in function_points], ensure_ascii=False, indent=2)}

请从以下几个方面进行审核，并生成详细的审核报告:

1. **需求完整性检查**
   - 检查需求描述是否完整
   - 检查是否有遗漏的功能点
   - 检查IR→SR分解是否合理

2. **二义性检查**
   - 识别可能存在歧义的描述
   - 提出澄清建议

3. **矛盾检查**
   - 检查需求之间是否存在矛盾
   - 检查功能点之间是否有冲突

4. **优先级合理性检查**
   - 评估优先级分配是否合理
   - 提出调整建议

5. **测试可行性评估**
   - 评估需求是否可测试
   - 提出测试建议

请以Markdown格式输出审核报告，包含具体的问题列表和改进建议。"""

        review = ai_service.generate(prompt)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="需求分析",
            content_summary=f"审核需求文档: {file_name}",
            status="成功",
            duration=duration,
            tokens_used=len(str(review)),
            project_id=project_id,
        )

        return jsonify({"success": True, "review": review})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "需求分析", "审核需求文档失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    """AI助手对话接口"""
    start_time = datetime.now()
    data = request.json
    message = data.get("message", "")
    context = data.get("context", {})
    history = data.get("history", [])

    if not message:
        return jsonify({"success": False, "error": "消息不能为空"}), 400

    try:
        ai_service = get_ai_service_from_config()

        # 构建系统提示
        system_prompt = f"""你是一个专业的车载控制器测试AI助手，帮助工程师完成测试相关工作。

当前上下文信息:
- 当前页面: {context.get("currentPage", "未知")}
- 项目名称: {context.get("projectName", "未打开项目")}
- 是否上传需求文件: {"是" if context.get("hasUploadedFile") else "否"}
- 功能点数量: {context.get("functionPointCount", 0)}

你可以帮助工程师:
1. 需求分析 - 解析需求文档，生成功能点
2. 测试策略 - 生成测试策略文档
3. 测试设计 - 生成测试设计方案
4. 测试用例 - 生成测试用例
5. 测试脚本 - 生成自动化测试脚本
6. 日志分析 - 分析测试日志
7. 测试评估 - 生成测试评估报告
8. 测试报告 - 生成测试报告

请根据工程师的问题和当前上下文，提供专业、准确的回答。如果工程师想要执行某个操作，请指导他们如何操作。"""

        # 构建对话历史
        conversation = []
        for h in history[-5:]:  # 最近5条历史
            conversation.append(f"{h['role']}: {h['content']}")

        prompt = f"{system_prompt}\n\n对话历史:\n{chr(10).join(conversation)}\n\n用户: {message}\n\n请用中文回答:"

        response = ai_service.generate(prompt)
        duration = (datetime.now() - start_time).total_seconds()

        record_ai_usage(
            skill_type="AI助手",
            content_summary=f"对话: {message[:50]}",
            status="成功",
            duration=duration,
            tokens_used=len(response),
            project_id=context.get("projectName"),
        )

        return jsonify({"success": True, "response": response})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage("AI助手", "对话失败", "失败", duration)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/optimize-testcases", methods=["POST"])
def optimize_testcases():
    """根据审核意见优化测试用例"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")
    testcases = data.get("testcases", [])
    review_comment = data.get("review_comment", "")

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    try:
        ai_service = get_ai_service_from_config()

        prompt = f"""你是一个专业的测试工程师，请根据审核意见优化以下测试用例。

当前测试用例:
{json.dumps(testcases, ensure_ascii=False, indent=2)}

审核意见:
{review_comment}

请根据审核意见优化测试用例，返回优化后的测试用例JSON数组。每个用例应包含:
- id: 用例ID
- name: 用例名称
- priority: 优先级(P0/P1/P2)
- precondition: 前置条件
- input: 测试输入
- expected: 预期输出
- auto: 是否可自动化(true/false)
- steps: 测试步骤

只返回JSON数组，不要其他说明文字。"""

        response = ai_service.generate(prompt)
        duration = (datetime.now() - start_time).total_seconds()

        # 尝试解析JSON
        try:
            if "[" in response and "]" in response:
                start = response.index("[")
                end = response.rindex("]") + 1
                json_str = response[start:end]
                optimized_testcases = json.loads(json_str)
            else:
                optimized_testcases = testcases
        except:
            optimized_testcases = testcases

        record_ai_usage(
            skill_type="用例生成",
            content_summary=f"优化测试用例: {review_comment[:50]}",
            status="成功",
            duration=duration,
            tokens_used=len(response),
            project_id=project_id,
        )

        return jsonify({"success": True, "testcases": optimized_testcases})
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            "用例生成", "优化测试用例失败", "失败", duration, project_id=project_id
        )
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== AI服务实现 ====================


def generate_test_strategy_ai(requirements, system_design, skills, engineer_req):
    """生成测试策略文档 - 使用AI服务"""
    ai_service = get_ai_service_from_config()

    prompt = f"""你是一个专业的车载控制器测试工程师，请根据以下需求生成详细的测试策略文档。

需求内容：
{requirements}

系统设计：
{system_design if system_design else "未提供"}

测试技能要求：
{", ".join(skills) if skills else "标准测试技能"}

请生成完整的测试策略文档，包含：测试范围、测试策略、测试环境、测试进度、风险应对。使用Markdown格式。"""

    try:
        return ai_service.generate(prompt, max_tokens=4000)
    except Exception as e:
        print(f"AI error: {e}")
        return f"# 测试策略文档\n\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def generate_test_design_ai(requirements):
    """生成测试设计文档 - 使用AI服务"""
    ai_service = get_ai_service_from_config()

    prompt = f"""你是一个专业的测试工程师，请根据以下需求生成测试设计文档。

需求内容：
{requirements}

请为每个主要功能模块生成测试设计，包含：测试设计ID、名称、类型、优先级、前置条件、测试方法、验收标准。使用Markdown格式。"""

    try:
        result = ai_service.generate(prompt, max_tokens=4000)
        return [result]
    except Exception as e:
        print(f"AI error: {e}")
        return ["测试设计生成失败，请检查AI配置"]


def generate_testcases_ai(requirements, designs):
    """生成测试用例 - 使用AI服务"""
    ai_service = get_ai_service_from_config()

    prompt = f"""你是一个专业的测试工程师，请根据以下需求和设计生成详细的测试用例。

需求内容：
{requirements}

测试设计：
{designs if designs else "未提供"}

请生成测试用例JSON数组，每个用例必须包含以下字段：
- id: 用例ID (如 TC001, TC002)
- name: 用例名称
- module: 所属模块
- priority: 优先级 (P0/P1/P2)
- precondition: 前置条件
- input: 测试输入数据
- steps: 测试步骤描述
- expected: 预期输出结果
- auto: 是否可自动化 (true/false)

只返回JSON数组，不要其他说明文字。"""

    try:
        result = ai_service.generate(prompt, max_tokens=4000)
        import json
        import re

        json_match = re.search(r"\[.*\]", result, re.DOTALL)
        if json_match:
            testcases = json.loads(json_match.group())
            # 确保每个用例都有必要字段
            for i, tc in enumerate(testcases):
                tc.setdefault("id", f"TC{str(i + 1).zfill(3)}")
                tc.setdefault("name", f"测试用例{i + 1}")
                tc.setdefault("module", "通用")
                tc.setdefault("priority", "P2")
                tc.setdefault("precondition", "无")
                tc.setdefault("input", "无")
                tc.setdefault("steps", "无")
                tc.setdefault("expected", "无")
                tc.setdefault("auto", True)
            return testcases
        return [
            {
                "id": "TC001",
                "name": "基础功能测试",
                "module": "通用",
                "priority": "P1",
                "precondition": "系统正常运行",
                "input": "正常输入数据",
                "steps": "执行测试操作",
                "expected": "功能正常工作",
                "auto": True,
            }
        ]
    except Exception as e:
        print(f"AI error: {e}")
        return []


def generate_scripts_ai(testcases, framework="pytest"):
    """生成测试脚本 - 使用AI服务"""
    ai_service = get_ai_service_from_config()

    prompt = f"""你是一个专业的测试开发工程师，请根据以下测试用例生成{framework}测试脚本。

测试用例：
{testcases}

请生成完整的Python测试脚本，包含import、测试类、测试方法、断言。输出可运行的代码。"""

    try:
        result = ai_service.generate(prompt, max_tokens=4000)
        return [
            {
                "name": "test_generated.py",
                "language": "python",
                "framework": framework,
                "content": result,
            }
        ]
    except Exception as e:
        print(f"AI error: {e}")
        return [
            {
                "name": "test_placeholder.py",
                "language": "python",
                "framework": framework,
                "content": "# 脚本生成失败\nimport pytest\n\ndef test_placeholder():\n    assert True",
            }
        ]


def parse_log_ai(log_content):
    """解析测试日志 - 使用AI服务"""
    ai_service = get_ai_service_from_config()

    prompt = f"""你是一个专业的测试分析师，请分析以下测试日志并提取关键信息。

日志内容：
{log_content[:5000]}

请分析并输出：测试概要、失败详情、异常事件、性能指标、问题建议。使用JSON格式。"""

    try:
        result = ai_service.generate(prompt, max_tokens=3000)
        return result
    except Exception as e:
        print(f"AI error: {e}")
        return {"summary": "日志解析失败", "error": str(e)}

        # 统计测试结果
        if "PASSED" in line or "passed" in line:
            parsed["summary"]["passed"] += 1
            parsed["summary"]["total_tests"] += 1
        elif "FAILED" in line or "failed" in line:
            parsed["summary"]["failed"] += 1
            parsed["summary"]["total_tests"] += 1
        elif "ERROR" in line:
            parsed["summary"]["errors"] += 1

        # 提取DTC
        if "DTC" in line or "故障码" in line:
            import re

            dtc_match = re.findall(r"[A-Z0-9]{{6}}", line)
            parsed["dtc_codes"].extend(dtc_match)

        # 提取警告
        if "WARNING" in line or "警告" in line:
            parsed["warnings"].append(line)

        # 提取错误
        if "ERROR" in line or "错误" in line:
            parsed["errors"].append(line)

    parsed["dtc_codes"] = list(set(parsed["dtc_codes"]))  # 去重

    return parsed


def generate_evaluation_ai(test_results, metrics):
    """生成测试评估报告 - 使用AI服务"""
    ai_service = get_ai_service_from_config()

    prompt = f"""你是一个专业的测试评估师，请根据以下测试结果生成评估报告。

测试结果：
{test_results}

指标数据：
{metrics}

请生成评估报告，包含：测试完成度、质量指标、风险评估、改进建议。使用Markdown格式。"""

    try:
        return ai_service.generate(prompt, max_tokens=3000)
    except Exception as e:
        print(f"AI error: {e}")
        return f"# 测试评估报告\n\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def generate_report_ai(project_id, report_type):
    """生成测试报告 - 使用AI服务"""
    ai_service = get_ai_service_from_config()

    projects = load_projects()
    project = projects.get(project_id, {})

    prompt = f"""你是一个专业的测试报告撰写师，请根据以下项目信息生成{report_type}。

项目信息：
- 项目名称：{project.get("name", "未知项目")}
- 需求：{project.get("requirements", {})}
- 测试用例：{project.get("testcases", [])}

请生成完整的测试报告，包含：报告概要、测试范围、测试结果、问题风险、结论建议。使用Markdown格式。"""

    try:
        return ai_service.generate(prompt, max_tokens=5000)
    except Exception as e:
        print(f"AI error: {e}")
        return f"# {report_type}\n\n项目：{project.get('name', '未知项目')}\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def analyze_requirements_ai(content):
    """分析需求文档 - 使用AI服务提取功能点"""
    # Get AI service
    ai_service = get_ai_service_from_config()

    # If no content, return empty result
    if not content or len(content.strip()) < 10:
        return {
            "summary": "需求内容不足，无法分析",
            "functional_count": 0,
            "non_functional_count": 0,
            "functional_requirements": [],
            "non_functional_requirements": [],
            "analyzed_at": datetime.now().isoformat(),
        }

    # Use AI to analyze requirements - improved prompt for better extraction
    prompt = f"""你是一个专业的需求分析师，请仔细分析以下需求文档，提取所有功能需求点。

需求文档内容：
{content[:6000]}

请按以下要求提取功能需求：

1. 每个功能需求应包含：
   - name: 功能名称（简洁明了，不超过30字）
   - description: 功能描述（详细说明该功能的具体要求）
   - category: 功能分类（如：数据管理、数据分析、报告生成、可视化、权限管理等）
   - priority: 优先级（P0/P1/P2，P0最高）

2. 提取规则：
   - 关注"功能需求"章节中的每个功能点
   - 每个子功能点应单独列出
   - 功能描述应包含具体的输入输出和处理逻辑
   - 按功能模块进行分类

3. 输出格式（JSON）：
{{
    "functional_requirements": [
        {{
            "name": "功能名称",
            "description": "详细功能描述",
            "category": "功能分类",
            "priority": "P0/P1/P2"
        }}
    ],
    "non_functional_requirements": [
        {{
            "name": "非功能需求名称",
            "description": "详细描述",
            "category": "性能/安全/可靠性等"
        }}
    ],
    "summary": "需求分析总结"
}}

请确保输出为有效的JSON格式。"""

    try:
        result = ai_service.generate(prompt, max_tokens=4000)

        # Try to parse JSON from result
        import re
        import json

        # Find JSON block in result
        json_match = re.search(r"\{[\s\S]*\}", result)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                functional_reqs = parsed.get("functional_requirements", [])
                non_functional_reqs = parsed.get("non_functional_requirements", [])
                summary = parsed.get("summary", "")
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                json_str = json_match.group()
                json_str = json_str.replace("'", '"')
                json_str = re.sub(r",\s*}", "}", json_str)
                json_str = re.sub(r",\s*]", "]", json_str)
                try:
                    parsed = json.loads(json_str)
                    functional_reqs = parsed.get("functional_requirements", [])
                    non_functional_reqs = parsed.get("non_functional_requirements", [])
                    summary = parsed.get("summary", "")
                except:
                    functional_reqs = []
                    non_functional_reqs = []
                    summary = result[:500]
        else:
            # Fallback: extract from text using patterns
            functional_reqs = []
            non_functional_reqs = []
            summary = "无法解析AI返回结果"

            # Try to extract function names from text
            lines = result.split("\n")
            for line in lines:
                line = line.strip()
                if line and len(line) > 5:
                    # Look for numbered items or bullet points
                    if re.match(r"^[\d\-\•\*\.]+\s*", line):
                        clean_line = re.sub(r"^[\d\-\•\*\.\s]+", "", line)
                        if clean_line:
                            functional_reqs.append(
                                {
                                    "name": clean_line[:50],
                                    "description": clean_line,
                                    "category": "功能需求",
                                    "priority": "P1",
                                }
                            )

        return {
            "summary": summary
            or f"分析发现{len(functional_reqs)}个功能需求，{len(non_functional_reqs)}个非功能需求",
            "functional_count": len(functional_reqs),
            "non_functional_count": len(non_functional_reqs),
            "functional_requirements": functional_reqs[:30],
            "non_functional_requirements": non_functional_reqs[:15],
            "analyzed_at": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"AI analysis error: {e}")
        import traceback

        traceback.print_exc()

        # Fallback: extract from content directly
        functional_reqs = []
        non_functional_reqs = []

        # Parse markdown headers and content
        lines = content.split("\n")
        current_section = ""
        current_content = []

        for line in lines:
            if line.startswith("### ") or line.startswith("#### "):
                # Save previous section
                if current_section and current_content:
                    section_text = " ".join(current_content)
                    if any(
                        kw in current_section.lower()
                        for kw in ["功能", "function", "feature"]
                    ):
                        functional_reqs.append(
                            {
                                "name": current_section.replace("#", "").strip(),
                                "description": section_text[:500],
                                "category": "功能需求",
                                "priority": "P1",
                            }
                        )
                    elif any(
                        kw in current_section.lower()
                        for kw in ["性能", "安全", "可靠", "非功能"]
                    ):
                        non_functional_reqs.append(
                            {
                                "name": current_section.replace("#", "").strip(),
                                "description": section_text[:500],
                                "category": "非功能需求",
                            }
                        )

                current_section = line
                current_content = []
            else:
                current_content.append(line)

        return {
            "summary": f"分析发现{len(functional_reqs)}个功能需求，{len(non_functional_reqs)}个非功能需求（本地解析）",
            "functional_count": len(functional_reqs),
            "non_functional_count": len(non_functional_reqs),
            "functional_requirements": functional_reqs[:20],
            "non_functional_requirements": non_functional_reqs[:10],
            "analyzed_at": datetime.now().isoformat(),
        }

    # Use AI to analyze requirements
    prompt = f"""请分析以下需求文档，提取功能需求和非功能需求。

需求文档内容：
{content[:3000]}

请按以下格式输出：
1. 功能需求列表（每个需求包含：名称、描述）
2. 非功能需求列表（每个需求包含：名称、描述）

请用JSON格式输出：
{{
    "functional_requirements": [
        {{"name": "需求名称", "description": "需求描述"}},
        ...
    ],
    "non_functional_requirements": [
        {{"name": "需求名称", "description": "需求描述"}},
        ...
    ]
}}
"""

    try:
        result = ai_service.generate(prompt, max_tokens=2000)

        # Try to parse JSON from result
        import re

        json_match = re.search(r"\{[\s\S]*\}", result)
        if json_match:
            import json

            parsed = json.loads(json_match.group())
            functional_reqs = parsed.get("functional_requirements", [])
            non_functional_reqs = parsed.get("non_functional_requirements", [])
        else:
            # Fallback: extract from text
            functional_reqs = []
            non_functional_reqs = []
            lines = content.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if line and len(line) > 5:
                    if any(
                        kw in line
                        for kw in ["shall", "应该", "必须", "需要", "支持", "功能"]
                    ):
                        functional_reqs.append(
                            {
                                "name": line[:50] + "..." if len(line) > 50 else line,
                                "description": line,
                            }
                        )
                    if any(
                        kw in line
                        for kw in ["性能", "响应", "可靠", "安全", "时间", "效率"]
                    ):
                        non_functional_reqs.append(
                            {
                                "name": line[:50] + "..." if len(line) > 50 else line,
                                "description": line,
                            }
                        )

        return {
            "summary": f"分析发现{len(functional_reqs)}个功能需求，{len(non_functional_reqs)}个非功能需求",
            "functional_count": len(functional_reqs),
            "non_functional_count": len(non_functional_reqs),
            "functional_requirements": functional_reqs[:15],
            "non_functional_requirements": non_functional_reqs[:10],
            "analyzed_at": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"AI analysis error: {e}")
        # Fallback to keyword extraction
        functional_reqs = []
        non_functional_reqs = []
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:
                if any(
                    kw in line
                    for kw in ["shall", "应该", "必须", "需要", "支持", "功能"]
                ):
                    functional_reqs.append(
                        {
                            "name": line[:50] + "..." if len(line) > 50 else line,
                            "description": line,
                        }
                    )
                if any(kw in line for kw in ["性能", "响应", "可靠", "安全"]):
                    non_functional_reqs.append(
                        {
                            "name": line[:50] + "..." if len(line) > 50 else line,
                            "description": line,
                        }
                    )

        return {
            "summary": f"分析发现{len(functional_reqs)}个功能需求，{len(non_functional_reqs)}个非功能需求",
            "functional_count": len(functional_reqs),
            "non_functional_count": len(non_functional_reqs),
            "functional_requirements": functional_reqs[:10],
            "non_functional_requirements": non_functional_reqs[:5],
            "analyzed_at": datetime.now().isoformat(),
        }


def review_report_ai(report_content):
    """审查测试报告 - 使用AI服务"""
    ai_service = get_ai_service_from_config()

    prompt = f"""你是一个专业的质量审核员，请审查以下测试报告。

报告内容：
{report_content}

请审查并输出：完整性评估、准确性评估、规范性评估、问题列表、改进建议。使用JSON格式。"""

    try:
        result = ai_service.generate(prompt, max_tokens=2000)
        return result
    except Exception as e:
        print(f"AI error: {e}")
        return {
            "review_status": "审查失败",
            "issues": [str(e)],
            "suggestions": [],
            "overall_quality": "未知",
        }


def optimize_script_ai(script_content):
    """优化测试脚本 - 使用AI服务"""
    ai_service = get_ai_service_from_config()

    prompt = f"""你是一个专业的测试开发工程师，请优化以下测试脚本。

脚本内容：
{script_content}

请优化并输出：代码结构优化、性能优化、可读性优化、错误处理优化。输出优化后的完整代码。"""

    try:
        return ai_service.generate(prompt, max_tokens=4000)
    except Exception as e:
        print(f"AI error: {e}")
        return script_content + "\n# 优化失败，返回原始脚本"


# ==================== 看板API ====================


@app.route("/api/benchmarks", methods=["GET"])
def get_benchmarks():
    """获取测试台架列表"""
    return jsonify(
        {
            "success": True,
            "benchmarks": [
                {"id": "B001", "name": "HIL台架1", "status": "空闲", "lab": "Lab-A"},
                {"id": "B002", "name": "HIL台架2", "status": "使用中", "lab": "Lab-A"},
                {
                    "id": "B003",
                    "name": "实车测试台架",
                    "status": "空闲",
                    "lab": "Lab-B",
                },
            ],
        }
    )


@app.route("/api/benchmarks", methods=["POST"])
def add_benchmark():
    """添加测试台架"""
    data = request.json
    return jsonify(
        {
            "success": True,
            "id": str(uuid.uuid4()),
            "name": data.get("name", "新台架"),
            "status": "空闲",
        }
    )


@app.route("/api/automation/jobs", methods=["GET"])
def get_automation_jobs():
    """获取自动化任务列表"""
    return jsonify(
        {
            "success": True,
            "jobs": [
                {
                    "id": "J001",
                    "name": "每日构建测试",
                    "status": "已完成",
                    "last_run": "2026-04-04 08:00",
                },
                {
                    "id": "J002",
                    "name": "回归测试",
                    "status": "运行中",
                    "last_run": "2026-04-04 10:00",
                },
                {
                    "id": "J003",
                    "name": "性能测试",
                    "status": "等待中",
                    "last_run": "2026-04-03 14:00",
                },
            ],
        }
    )


@app.route("/api/automation/jobs", methods=["POST"])
def create_automation_job():
    """创建自动化任务"""
    data = request.json
    return jsonify(
        {
            "success": True,
            "id": str(uuid.uuid4()),
            "name": data.get("name", "新任务"),
            "status": "等待中",
        }
    )


@app.route("/api/automation/jobs/<job_id>/run", methods=["POST"])
def run_automation_job(job_id):
    """执行自动化任务"""
    return jsonify({"success": True, "message": f"任务 {job_id} 已启动"})


# ==================== AI配置API ====================


@app.route("/api/ai/config", methods=["GET"])
def get_ai_config():
    """获取AI配置"""
    config = load_ai_config()
    # 隐藏API Key的部分内容
    safe_config = config.copy()
    if safe_config.get("api_key"):
        key = safe_config["api_key"]
        safe_config["api_key_masked"] = (
            key[:8] + "***" + key[-4:] if len(key) > 12 else "***"
        )
    return jsonify({"success": True, "config": safe_config})


@app.route("/api/ai/config", methods=["POST"])
def update_ai_config():
    """更新AI配置"""
    data = request.json

    config = load_ai_config()

    # 更新配置
    if "provider" in data:
        config["provider"] = data["provider"]
    if "model" in data:
        config["model"] = data["model"]
    if "api_key" in data and data["api_key"]:
        config["api_key"] = data["api_key"]
    if "base_url" in data:
        config["base_url"] = data["base_url"]
    if "max_tokens" in data:
        config["max_tokens"] = int(data["max_tokens"])
    if "temperature" in data:
        config["temperature"] = float(data["temperature"])

    save_ai_config(config)

    return jsonify({"success": True, "message": "AI配置已更新"})


@app.route("/api/ai/test", methods=["POST"])
def test_ai_connection():
    """测试AI连接"""
    try:
        ai_service = get_ai_service_from_config()
        result = ai_service.generate("测试连接：请回复'连接成功'", max_tokens=50)
        return jsonify(
            {
                "success": True,
                "message": "AI连接测试成功",
                "response": result[:100] if result else None,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ==================== 健康检查 ====================


@app.route("/api/health", methods=["GET"])
def health_check():
    """健康检查接口"""
    config = load_ai_config()
    return jsonify(
        {
            "status": "healthy",
            "service": "VehicleTestAI Backend",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "ai_provider": config.get("provider", "mock"),
            "ai_model": config.get("model", "unknown"),
        }
    )


# ==================== DBC解析与日志分析 ====================

# DBC服务缓存（存储已解析的DBC）
DBC_CACHE = {}


@app.route("/api/dbc/parse", methods=["POST"])
def parse_dbc():
    """解析DBC文件"""
    data = request.json
    dbc_content = data.get("content", "")
    dbc_name = data.get("name", "unknown.dbc")
    project_id = data.get("project_id")

    if not dbc_content:
        return jsonify({"success": False, "error": "DBC文件内容为空"}), 400

    try:
        from services.dbc_service import dbc_service

        result = dbc_service.parse_dbc_file(dbc_content, dbc_name)

        if result["success"]:
            # 缓存DBC解析结果
            cache_key = f"{project_id}_{dbc_name}" if project_id else dbc_name
            DBC_CACHE[cache_key] = {
                "db": dbc_service.dbc_cache.get(dbc_name, {}).get("db"),
                "messages": result["messages"],
                "signals": result["signals"],
            }

            # 保存到项目
            if project_id:
                projects = load_projects()
                if project_id in projects:
                    if "dbc_files" not in projects[project_id]:
                        projects[project_id]["dbc_files"] = {}
                    projects[project_id]["dbc_files"][dbc_name] = {
                        "name": dbc_name,
                        "message_count": result["message_count"],
                        "signal_count": result["signal_count"],
                        "parsed_at": result["parsed_at"],
                    }
                    save_projects(projects)

        return jsonify(result)
    except ImportError as e:
        return jsonify(
            {"success": False, "error": f"缺少依赖: {str(e)}，请安装cantools"}
        ), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dbc/list/<project_id>", methods=["GET"])
def list_project_dbc(project_id):
    """获取项目的DBC文件列表"""
    projects = load_projects()
    if project_id not in projects:
        return jsonify({"success": False, "error": "项目不存在"}), 404

    dbc_files = projects[project_id].get("dbc_files", {})
    return jsonify({"success": True, "dbc_files": dbc_files})


@app.route("/api/logs/analyze-with-dbc", methods=["POST"])
def analyze_logs_with_dbc():
    """使用DBC定义分析日志"""
    start_time = datetime.now()
    data = request.json
    project_id = data.get("project_id")
    log_content = data.get("log_content", "")
    log_format = data.get("log_format", "asc")
    dbc_name = data.get("dbc_name")
    testcases = data.get("testcases", [])
    tolerance = data.get("tolerance", 0.05)

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    if not log_content:
        return jsonify({"success": False, "error": "日志内容为空"}), 400

    try:
        from services.log_analysis_service import log_analysis_service
        from services.dbc_service import dbc_service

        # 1. 解析日志文件
        log_result = log_analysis_service.parse_log_file(log_content, log_format)

        if not log_result["success"]:
            return jsonify(log_result), 500

        # 2. 如果有DBC，提取信号
        signal_extraction = {"signals": {}, "signal_stats": {}}

        if dbc_name:
            cache_key = f"{project_id}_{dbc_name}"
            if cache_key in DBC_CACHE or dbc_name in dbc_service.dbc_cache:
                dbc_cache_key = (
                    dbc_name if dbc_name in dbc_service.dbc_cache else cache_key
                )
                signal_extraction = log_analysis_service.extract_signals_with_dbc(
                    log_result.get("messages", []), dbc_cache_key, dbc_service.dbc_cache
                )

        # 3. 如果有测试用例，进行匹配
        testcase_match = {"results": [], "total_testcases": 0, "passed": 0, "failed": 0}

        if testcases and signal_extraction.get("signals"):
            testcase_match = log_analysis_service.match_with_testcases(
                signal_extraction["signals"], testcases, tolerance
            )

        # 4. 生成分析报告
        log_info = {
            "name": data.get("log_name", "unknown.log"),
            "format": log_format,
            "message_count": log_result.get("message_count", 0),
            "errors": log_result.get("errors", 0),
            "dtcs": log_result.get("dtcs", 0),
        }

        dbc_info = {
            "dbc_name": dbc_name or "未使用",
            "message_count": len(signal_extraction.get("signal_stats", {})),
            "signal_count": signal_extraction.get("signal_count", 0),
        }

        report = log_analysis_service.generate_analysis_report(
            log_info, dbc_info, signal_extraction, testcase_match
        )

        # 5. 保存结果到项目
        projects = load_projects()
        if project_id in projects:
            analysis_result = {
                "log_info": log_info,
                "dbc_info": dbc_info,
                "signal_extraction": {
                    "signal_count": signal_extraction.get("signal_count", 0),
                    "signal_stats": signal_extraction.get("signal_stats", {}),
                },
                "testcase_match": {
                    "total": testcase_match.get("total_testcases", 0),
                    "passed": testcase_match.get("passed", 0),
                    "failed": testcase_match.get("failed", 0),
                    "pass_rate": testcase_match.get("pass_rate", 0),
                },
                "report": report,
                "analyzed_at": datetime.now().isoformat(),
            }

            if "log_analysis" not in projects[project_id]:
                projects[project_id]["log_analysis"] = []
            projects[project_id]["log_analysis"].append(analysis_result)
            projects[project_id]["updated"] = datetime.now().isoformat()
            save_projects(projects)

            # 保存报告到磁盘
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"log_analysis_{timestamp}.md"
            save_ai_content_to_disk(project_id, "log", filename, report)

        # 记录AI使用
        duration = (datetime.now() - start_time).total_seconds()
        record_ai_usage(
            skill_type="日志分析",
            content_summary=f"分析日志并提取{signal_extraction.get('signal_count', 0)}个信号",
            status="成功",
            duration=duration,
            tokens_used=len(report),
            project_id=project_id,
        )

        return jsonify(
            {
                "success": True,
                "log_info": log_info,
                "signal_extraction": {
                    "signal_count": signal_extraction.get("signal_count", 0),
                    "signals": list(signal_extraction.get("signals", {}).keys())[
                        :20
                    ],  # 只返回信号名列表
                    "signal_stats": signal_extraction.get("signal_stats", {}),
                },
                "testcase_match": testcase_match,
                "report": report,
            }
        )

    except ImportError as e:
        return jsonify({"success": False, "error": f"缺少依赖: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/logs/signal-list/<project_id>", methods=["GET"])
def get_signal_list(project_id):
    """获取项目可用的信号列表（从DBC）"""
    projects = load_projects()
    if project_id not in projects:
        return jsonify({"success": False, "error": "项目不存在"}), 404

    dbc_files = projects[project_id].get("dbc_files", {})
    signals = []

    for dbc_name, dbc_info in dbc_files.items():
        cache_key = f"{project_id}_{dbc_name}"
        if cache_key in DBC_CACHE:
            signals.extend([s["name"] for s in DBC_CACHE[cache_key].get("signals", [])])

    return jsonify(
        {
            "success": True,
            "signals": list(set(signals)),  # 去重
            "signal_count": len(set(signals)),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
