from flask import Blueprint, request, jsonify
import os
import uuid
from datetime import datetime

from models import db, Project

# 蓝图：项目管理 API
project_bp = Blueprint("project_routes", __name__)


@project_bp.route("/api/projects", methods=["GET"])
def get_projects():
    """获取项目列表"""
    try:
        projects = Project.query.all()
        return jsonify({"success": True, "projects": [p.to_dict() for p in projects]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@project_bp.route("/api/projects", methods=["POST"])
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
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@project_bp.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    """获取项目详情"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404
        return jsonify({"success": True, "project": project.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@project_bp.route("/api/projects/<project_id>", methods=["PUT"])
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


@project_bp.route("/api/projects/<project_id>", methods=["DELETE"])
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


@project_bp.route("/api/projects/<project_id>/sync", methods=["POST"])
def sync_project(project_id):
    """同步项目文件"""
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
