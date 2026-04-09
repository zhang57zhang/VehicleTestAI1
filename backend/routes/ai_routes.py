from flask import Blueprint, request, jsonify

# 注意: 该模块依赖服务层的 AI 实现，尽量复用已有服务逻辑
from models import db, Project, Requirement, TestStrategy, TestDesign, TestCase, TestLog
from services.ai_service import get_ai_service, GLMService, get_configured_ai_service
from datetime import datetime

ai_bp = Blueprint("ai_routes", __name__)


@ai_bp.route("/api/ai/config", methods=["GET"])
def get_ai_config():
    """获取AI配置信息"""
    # 演示性实现，与原实现等价
    ZHIPUAI_API_KEY = __import__("os").environ.get("GLM_API_KEY") or __import__(
        "os"
    ).environ.get("ZHIPUAI_API_KEY")
    ZHIPUAI_MODEL = __import__("os").environ.get("GLM_MODEL") or __import__(
        "os"
    ).environ.get("ZHIPUAI_MODEL", "glm-4.7")
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


@ai_bp.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    """AI助手对话"""
    try:
        data = request.json
        message = data.get("message", "")
        history = data.get("history", [])

        ai_service = get_configured_ai_service()
        system_prompt = "你是一个专业的车载控制器测试AI助手。你可以帮助工程师进行需求分析、测试策略制定、测试用例设计、测试脚本生成、日志分析和测试报告生成。请根据用户的问题提供专业、准确的回答，用中文回答。"
        full_prompt = f"{system_prompt}\n\n"
        if history:
            for h in history:
                role = "用户" if h.get("role") == "user" else "助手"
                full_prompt += f"{role}: {h.get('content', '')}\n"
            full_prompt += "\n"
        full_prompt += f"用户: {message}\n\n请回答："
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


@ai_bp.route("/api/ai/generate-strategy", methods=["POST"])
def generate_strategy():
    try:
        data = request.json
        project_id = data.get("project_id")
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        if requirements:
            req_text = "\n".join(
                [f"{r.id}: {r.name}\n{r.description}" for r in requirements]
            )
        elif data.get("requirements"):
            req_text = data.get("requirements")
        else:
            req_text = "请生成一个通用的 VCU 测试策略"
        ai_service = get_configured_ai_service()
        prompt = f"请根据以下需求生成测试策略：\n\n{req_text}"
        content = ai_service.generate(prompt)
        strategy_id = __import__("uuid").uuid4().__str__()
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


@ai_bp.route("/api/ai/generate-design", methods=["POST"])
def generate_design():
    try:
        data = request.json
        project_id = data.get("project_id")
        strategies = TestStrategy.query.filter_by(project_id=project_id).all()
        strategy_text = "\n\n".join([s.content for s in strategies])
        ai_service = get_configured_ai_service()
        prompt = f"请根据以下测试策略生成测试设计：\n\n{strategy_text}"
        content = ai_service.generate(prompt)
        design_id = __import__("uuid").uuid4().__str__()
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


@ai_bp.route("/api/ai/generate-testcases", methods=["POST"])
def generate_testcases():
    try:
        data = request.json
        project_id = data.get("project_id")
        design_content = data.get("design", "")
        if not design_content:
            designs = TestDesign.query.filter_by(project_id=project_id).all()
            if designs:
                design_content = designs[-1].content
        if not design_content:
            design_content = "基于VCU测试需求生成测试用例"
        ai_service = get_configured_ai_service()
        prompt = f"请根据以下测试设计生成详细的测试用例，包括：\n1. 用例ID\n2. 用例名称\n3. 测试目的\n4. 前置条件\n5. 测试步骤\n6. 预期结果\n7. 优先级\n\n测试设计：\n{design_content}"
        content = ai_service.generate(prompt)
        testcase_id = __import__("uuid").uuid4().__str__()
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


@ai_bp.route("/api/ai/generate-scripts", methods=["POST"])
def generate_scripts():
    try:
        data = request.json
        project_id = data.get("project_id")
        testcases = data.get("testcases", "")
        if not testcases:
            testcases = TestCase.query.filter_by(project_id=project_id).all()
            testcases = "\n".join([tc.steps for tc in testcases]) if testcases else ""
        ai_service = get_configured_ai_service()
        prompt = f"请根据以下测试用例生成Python自动化测试脚本。\n{testcases}"
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


@ai_bp.route("/api/ai/parse-log", methods=["POST"])
def parse_log():
    try:
        data = request.json
        project_id = data.get("project_id")
        log_content = data.get("log_content", "")
        if not log_content:
            log_content = "模拟日志：测试执行完成，50个用例通过，2个失败"
        ai_service = get_configured_ai_service()
        prompt = f"请分析以下测试日志，提取关键信息：\n日志内容：\n{log_content}\n请输出：1. 测试摘要（通过/失败数量） 2. 发现的问题 3. 性能数据 4. 建议的改进措施"
        content = ai_service.generate(prompt)
        log_id = __import__("uuid").uuid4().__str__()
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


@ai_bp.route("/api/ai/generate-report", methods=["POST"])
def generate_report():
    try:
        data = request.json
        project_id = data.get("project_id")
        project = Project.query.get(project_id)
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        strategies = TestStrategy.query.filter_by(project_id=project_id).all()
        designs = TestDesign.query.filter_by(project_id=project_id).all()
        testcases = TestCase.query.filter_by(project_id=project_id).all()
        logs = TestLog.query.filter_by(project_id=project_id).all()
        report_data = f"""项目：{project.name if project else "未知"}
需求数量：{len(requirements)}
测试策略数量：{len(strategies)}
测试设计数量：{len(designs)}
测试用例数量：{len(testcases)}
测试日志数量：{len(logs)}
"""
        ai_service = get_configured_ai_service()
        prompt = f"请根据以下测试数据生成一份完整的测试报告：\n\n{report_data} 要求包含：1. 测试概述 2. 测试范围 3. 测试结果统计 4. 问题清单 5. 风险评估 6. 结论与建议；请使用Markdown格式输出。"
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


@ai_bp.route("/api/ai/parse-requirements", methods=["POST"])
def parse_requirements():
    try:
        data = request.json
        project_id = data.get("project_id")
        content = data.get("content", "")
        if not content:
            ai_service = get_configured_ai_service()
            requirements = Requirement.query.filter_by(project_id=project_id).all()
            req_text = "\n".join([f"- {r.name}: {r.description}" for r in requirements])
            content = ai_service.generate(f"分析以下需求：\n{req_text}")
        ai_service = get_configured_ai_service()
        prompt = f"分析以下需求：\n{content[:4000]}"
        result = ai_service.generate(prompt)
        return jsonify({"success": True, "analysis": {"raw_content": result}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/review-requirements", methods=["POST"])
def review_requirements():
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


@ai_bp.route("/api/ai/generate-evaluation", methods=["POST"])
def generate_evaluation():
    try:
        data = request.json
        project_id = data.get("project_id")
        ai_service = get_configured_ai_service()
        content = ai_service.generate(f"请为项目{project_id}生成测试评估")
        return jsonify({"success": True, "evaluation": {"content": content}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/generate-dts", methods=["POST"])
def generate_dts():
    try:
        data = request.json
        project_id = data.get("project_id")
        ai_service = get_configured_ai_service()
        content = ai_service.generate(f"请为项目{project_id}生成缺陷跟踪表")
        return jsonify({"success": True, "dts": content})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
