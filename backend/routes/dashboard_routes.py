"""看板与健康状态相关的路由。

提供系统健康检查、执行状态统计以及缺陷跟踪等看板数据接口。
"""

from flask import Blueprint, jsonify
from models import TestCase, TestDesign, TestStrategy, Requirement
from datetime import datetime

dashboard_bp = Blueprint("dashboard_routes", __name__)


@dashboard_bp.route("/api/health", methods=["GET"])
def health_check():
    """健康检查接口

    简单返回服务状态、版本、数据库等信息，便于运维快速确认服务可用性。
    """
    from datetime import datetime as dt

    return jsonify(
        {
            "status": "healthy",
            "service": "VehicleTestAI Backend",
            "version": "2.0.0",
            "database": "SQLite",
            "timestamp": dt.now().isoformat(),
        }
    )


@dashboard_bp.route("/api/test-results/<project_id>", methods=["GET"])
def get_test_results(project_id):
    """获取某一项目的测试结果汇总

    读取当前项目相关的测试日志并整理成易于消费的结果集合。
    参数：project_id
    返回：{success, results: [...]}
    """
    from models import TestLog

    try:
        logs = TestLog.query.filter_by(project_id=project_id).all()
        results = [
            {"id": l.id, "name": l.signal or "Unknown", "value": l.value} for l in logs
        ]
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route("/api/execution-status/<project_id>", methods=["GET"])
def get_execution_status(project_id):
    """获取项目的执行状态摘要

    返回需求、策略、设计、用例数量等指标，以及一个示例进度值。
    参数：project_id
    返回：状态字典或错误信息
    """
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


@dashboard_bp.route("/api/dts/<project_id>", methods=["GET"])
def get_dts(project_id):
    """获取缺陷跟踪表（DTS）信息

    将日志中的缺陷信息整理为缺陷条目列表，便于看板展示。
    参数：project_id
    返回：defects 列表 或 错误信息
    """
    from models import TestLog

    try:
        logs = TestLog.query.filter_by(project_id=project_id).all()
        defects = [
            {"id": l.id, "name": l.signal or "Unknown", "severity": "medium"}
            for l in logs
        ]
        return jsonify({"success": True, "defects": defects})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
