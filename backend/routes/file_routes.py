"""文件上传相关 API 路由。

提供对上传文件的处理与校验，确保文件类型在允许清单内，并将文件保存到项目工作目录中。
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid

from models import db

# 蓝图：文件上传相关 API
file_bp = Blueprint("file_routes", __name__)

UPLOAD_ROOT = "uploads"
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


def allowed_file_upload(filename):
    """检查上传的文件扩展名是否在允许列表中"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@file_bp.route("/api/upload/<project_id>/<file_type>", methods=["POST"])
def upload_file(project_id, file_type):
    """上传文件到指定项目及类别

    流程：校验请求中的文件、检查扩展名、保存到 uploads/{project_id}/{file_type}/ 目录。
    返回：文件信息字典，包括文件ID、路径和名称。
    出错时返回相应的错误信息。
    """
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400
        if file and allowed_file_upload(file.filename):
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            project_dir = os.path.join(UPLOAD_ROOT, project_id, file_type)
            os.makedirs(project_dir, exist_ok=True)
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
