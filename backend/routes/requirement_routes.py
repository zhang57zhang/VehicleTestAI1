"""后端需求路由：对需求 (Requirement) 的增删改查 API。"""

from flask import Blueprint, request, jsonify
import uuid

from models import db, Requirement

# 蓝图：需求管理 API
requirement_bp = Blueprint("requirement_routes", __name__)


@requirement_bp.route("/api/requirements/<project_id>", methods=["GET"])
def get_requirements(project_id):
    """获取指定项目的全部需求列表

    参数：project_id - 项目ID
    返回：包含需求字典列表的 JSON，这些字典通过 to_dict() 序列化。
    """
    try:
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        return jsonify(
            {"success": True, "requirements": [r.to_dict() for r in requirements]}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@requirement_bp.route("/api/requirements", methods=["POST"])
def create_requirement():
    """创建一个新的需求点

    请求体应包含以下字段：project_id, name, category, priority, description, source, linkedReqs
    返回：新创建的需求对象字典及 201 状态码
    """
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


@requirement_bp.route("/api/requirements/<req_id>", methods=["DELETE"])
def delete_requirement(req_id):
    """删除指定需求

    参数：req_id - 需求ID
    返回：删除成功标识或错误信息。
    """
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


@requirement_bp.route("/api/requirements/<req_id>", methods=["PUT"])
def update_requirement(req_id):
    """更新指定需求的字段

    允许更新的字段包括：name, description, category, priority
    返回：更新后的需求对象字典，失败时返回错误信息。
    """
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
