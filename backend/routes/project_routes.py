"""后端项目管理路由：提供对 Project 的增删改查等 API。

本模块仅添加中文注释和文档字符串，保持业务逻辑不变，确保可读性与可维护性。
"""

from flask import Blueprint, request, jsonify
import os
import uuid
from datetime import datetime

from models import db, Project

# 蓝图：项目管理 API
project_bp = Blueprint("project_routes", __name__)


@project_bp.route("/api/projects", methods=["GET"])
def get_projects():
    """获取项目列表

    功能：返回数据库中所有项目的列表，每个项目以字典形式序列化。
    请求：无特定参数。
    返回：{"success": true, "projects": [...] } 的 JSON 响应，包含所有项目信息。
    错误：出现异常时返回错误信息与 500 状态码。
    """
    try:
        projects = Project.query.all()
        return jsonify({"success": True, "projects": [p.to_dict() for p in projects]})
    except Exception as e:
        # 捕获并返回服务器内部错误
        return jsonify({"success": False, "error": str(e)}), 500


@project_bp.route("/api/projects", methods=["POST"])
def create_project():
    """创建一个新项目

    请求参数（JSON）：
      - name: 项目名称，若缺省使用 "未命名项目"
      - description: 项目描述，默认为空
    返回：成功时返回新的项目对象的字典表示，以及 201 状态码。
    失败时回滚事务并返回错误信息。
    """
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

        # 创建项目目录结构，用于后续文件的分类存放
        project_dir = os.path.join("uploads", project_id)
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
        # 回滚数据库事务，避免脏数据
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@project_bp.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    """获取指定项目的详细信息

    参数：
      - project_id: 项目的唯一标识
    返回：成功时返回 {project: {...}}，找不到则返回 404；发生异常返回 500。
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404
        return jsonify({"success": True, "project": project.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@project_bp.route("/api/projects/<project_id>", methods=["PUT"])
def update_project(project_id):
    """更新指定项目的基本信息

    请求参数（JSON）：
      - name: 新名称（可选）
      - description: 新描述（可选）
    返回：更新后的项目对象字典，失败时返回错误信息。
    """
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


@project_bp.route("/api/projects/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    """删除指定项目及其相关数据记录

    参数：project_id 需要删除的项目ID
    返回：删除成功的标记或错误信息。
    注：当前实现仅删除数据库记录，不删除实际的上传目录，若需要，请扩展该逻辑。
    """
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


@project_bp.route("/api/projects/<project_id>/sync", methods=["POST"])
def sync_project(project_id):
    """同步项目文件到前端可用的数据结构

    读取 uploads/{project_id} 目录下的文件结构，整理成字典后返回，便于前端显示与管理。
    参数：project_id - 待同步的项目ID
    返回：包含文件树的 JSON 对象及项目基本信息。遇错返回错误信息。
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404
        upload_dir = os.path.join("uploads", project_id)
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
