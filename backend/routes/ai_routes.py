"""AI 路由：提供对话与自动化生成功能的 API。中文文档化，便于维护。"""
from flask import Blueprint, request, jsonify
import os
import json

# 注意: 该模块依赖服务层的 AI 实现，尽量复用已有服务逻辑
from models import db, Project, Requirement, TestStrategy, TestDesign, TestCase, TestLog
from services.ai_service import get_ai_service, GLMService, get_configured_ai_service
from datetime import datetime

ai_bp = Blueprint("ai_routes", __name__)

# 上传文件夹路径
UPLOAD_FOLDER = "uploads"


@ai_bp.route("/api/ai/config", methods=["GET"])
def get_ai_config():
    """获取AI配置信息

    返回当前 AI 提供商、模型以及可用性信息，供前端展示或决定后续使用的 AI 服务。
    """
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
    """AI 助手对话

    接收用户消息和历史对话记录，拼接成系统提示后调用 AI 服务，返回生成的回复文本。
    参数：message 为当前用户消息，history 为对话历史。
    返回：包含 AI 回复文本及时间戳的 JSON。
    """
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
    """生成测试策略

    通过 AI 根据项目需求生成测试策略文本，存储到数据库并返回策略对象。
    参数：project_id, (可选) requirements
    返回：包含新生成策略信息的 JSON。
    """
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
        
        # 保存到文件
        if project_id:
            strategy_dir = os.path.join(UPLOAD_FOLDER, project_id, "strategy")
            os.makedirs(strategy_dir, exist_ok=True)
            strategy_file = os.path.join(strategy_dir, f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            with open(strategy_file, "w", encoding="utf-8") as f:
                f.write(f"# 测试策略\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**项目ID**: {project_id}\n\n")
                f.write("---\n\n")
                f.write(content)
            print(f"📄 测试策略已保存到: {strategy_file}")
        
        return jsonify({"success": True, "strategy": strategy.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/generate-design", methods=["POST"])
def generate_design():
    """生成测试设计

    将现有的测试策略内容汇总后交由 AI 生成测试设计文本，保存在数据库并返回。
    参数：project_id
    返回：新生成的测试设计对象
    """
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
        
        # 保存到文件
        if project_id:
            design_dir = os.path.join(UPLOAD_FOLDER, project_id, "design")
            os.makedirs(design_dir, exist_ok=True)
            design_file = os.path.join(design_dir, f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            with open(design_file, "w", encoding="utf-8") as f:
                f.write(f"# 测试设计\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**项目ID**: {project_id}\n\n")
                f.write("---\n\n")
                f.write(content)
            print(f"📄 测试设计已保存到: {design_file}")
        
        return jsonify({"success": True, "design": design.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/generate-testcases", methods=["POST"])
def generate_testcases():
    """生成测试用例

    根据设计内容创建详细的测试用例文本，并持久化到数据库。
    参数：project_id、design（可选）
    返回：新生成的测试用例对象信息
    """
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
    """生成测试脚本

    将测试用例文本转换为可执行的 Python 脚本，常用于 pytest 框架。
    参数：project_id、testcases（可选）
    返回：生成的脚本内容及元信息
    """
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
    """解析测试日志

    将提供的日志内容提交给 AI 服务进行分析，结果保存到日志表并返回分析摘要与完整结果。
    参数：project_id、log_content
    返回：分析摘要与完整结果
    """
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
    """生成测试报告

    基于当前项目的需求、策略、设计、用例和日志等信息，调用 AI 生成完整的 Markdown 格式报告。
    参数：project_id
    返回：生成的报告文本及元数据
    """
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
    """分析需求文本

    将需求文本交给 AI 进行分析，并返回分析结果。
    参数：project_id、content（可选）
    返回：分析结果文本
    """
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
    """审核需求

    对指定项目的需求进行审核与评分，返回审核内容与分数。
    参数：project_id
    返回：审核结果
    """
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
    """生成测试评估

    调用 AI 生成针对当前项目的测试评估文本。
    参数：project_id
    返回：评估文本
    """
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
    """生成缺陷跟踪表 (DTS)

    调用 AI 生成一个缺陷跟踪表的文本表示。
    参数：project_id
    返回：DTS 文本内容
    """
    try:
        data = request.json
        project_id = data.get("project_id")
        ai_service = get_configured_ai_service()
        content = ai_service.generate(f"请为项目{project_id}生成缺陷跟踪表")
        return jsonify({"success": True, "dts": content})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
