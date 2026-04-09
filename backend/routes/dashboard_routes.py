from flask import Blueprint, jsonify
from models import TestCase, TestDesign, TestStrategy, Requirement
from datetime import datetime

dashboard_bp = Blueprint("dashboard_routes", __name__)


@dashboard_bp.route("/api/health", methods=["GET"])
def health_check():
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
