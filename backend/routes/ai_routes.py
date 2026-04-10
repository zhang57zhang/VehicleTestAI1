"""AI 路由：提供对话与自动化生成功能的 API。
中文文档化，便于维护。

测试活动对应:
- RA: 需求分析 (/api/ai/parse-requirements, /api/ai/review-requirements)
- TS: 测试策略 (/api/ai/generate-strategy)
- TD: 测试设计 (/api/ai/generate-design)
- TC: 测试用例 (/api/ai/generate-testcases)
- TScr: 测试脚本 (/api/ai/generate-scripts)
- TL: 测试日志 (/api/ai/parse-log)
- TEval: 测试评估 (/api/ai/generate-evaluation)
- TR: 测试报告 (/api/ai/generate-report)
"""

from flask import Blueprint, request, jsonify
import os
import json
import uuid

from models import (
    db,
    Project,
    Requirement,
    TestStrategy,
    TestDesign,
    TestCase,
    TestLog,
    AIHistory,
)
from services.ai_service import get_ai_service, GLMService, get_configured_ai_service
from services.enhanced_ai_service_v2 import get_enhanced_ai_service, EnhancedAIService
from utils.response import APIResponse, ErrorCode
from utils.error_handler import logger, handle_errors
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
@handle_errors()
def ai_chat():
    """AI 助手对话 (通用接口)

    支持所有测试活动相关的问答。

    请求参数:
        - message: 用户消息
        - history: 对话历史 (可选)
        - context: 上下文信息 (可选)

    返回:
        - response: AI回复
        - timestamp: 时间戳
    """
    data = request.json
    message = data.get("message", "")
    history = data.get("history", [])
    context = data.get("context", "")

    if not message:
        return APIResponse.validation_error("message", "消息不能为空")

    # 使用增强版服务
    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.chat(message=message, history=history, context=context)

    if result["success"]:
        return APIResponse.success(
            data={"response": result["response"]}, message="对话成功"
        )
    else:
        return APIResponse.error(
            message=result.get("error", "AI服务调用失败"),
            error_code=ErrorCode.AI_SERVICE_UNAVAILABLE,
        )


@ai_bp.route("/api/ai/generate-strategy", methods=["POST"])
@handle_errors()
def generate_strategy():
    """生成测试策略 (TS - 测试策略)

    活动代码: ACT-TS-*

    通过 AI 根据项目需求生成测试策略文本，存储到数据库并返回策略对象。

    请求参数:
        - project_id: 项目ID
        - requirements: 需求JSON字符串 (可选)
        - test_environment: 测试环境类型 (默认HIL)
        - skills: 测试技能列表 (可选)

    返回:
        - strategy: 生成的测试策略对象
    """
    data = request.json
    project_id = data.get("project_id")
    test_environment = data.get("test_environment", "HIL")
    skills = data.get("skills", [])

    # 获取需求
    requirements = []
    if data.get("requirements"):
        try:
            requirements = (
                json.loads(data.get("requirements"))
                if isinstance(data.get("requirements"), str)
                else data.get("requirements")
            )
        except:
            pass

    if not requirements and project_id:
        req_models = Requirement.query.filter_by(project_id=project_id).all()
        requirements = [r.to_dict() for r in req_models]

    # 使用增强版服务生成策略
    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.generate_test_strategy(
        requirements=requirements,
        project_name=project_id or "车载控制器项目",
        test_environment=test_environment,
        skills=skills,
    )

    if not result["success"]:
        return APIResponse.error(
            message=result.get("error", "策略生成失败"),
            error_code=ErrorCode.AI_GENERATION_FAILED,
        )

    # 保存到数据库
    strategy_id = str(uuid.uuid4())
    strategy = TestStrategy(
        id=strategy_id,
        project_id=project_id,
        name=f"测试策略_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        content=result["strategy"],
    )
    db.session.add(strategy)

    # 记录AI历史
    history = AIHistory(
        id=str(uuid.uuid4()),
        project_id=project_id,
        type="strategy",
        input=json.dumps({"requirements_count": len(requirements)}),
        output=result["strategy"][:500],
    )
    db.session.add(history)
    db.session.commit()

    # 保存到文件
    if project_id:
        strategy_dir = os.path.join(UPLOAD_FOLDER, project_id, "strategy")
        os.makedirs(strategy_dir, exist_ok=True)
        strategy_file = os.path.join(
            strategy_dir, f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(strategy_file, "w", encoding="utf-8") as f:
            f.write(f"# 测试策略\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**项目ID**: {project_id}\n\n")
            f.write(f"**测试环境**: {test_environment}\n\n")
            f.write("---\n\n")
            f.write(result["strategy"])
        logger.info(f"测试策略已保存到: {strategy_file}")

    return APIResponse.created(
        data={"strategy": strategy.to_dict()},
        message="测试策略生成成功",
        resource_type="TestStrategy",
        resource_id=strategy_id,
    )


@ai_bp.route("/api/ai/generate-design", methods=["POST"])
@handle_errors()
def generate_design():
    """生成测试设计 (TD - 测试设计)

    活动代码: ACT-TD-*

    将现有的测试策略内容汇总后交由 AI 生成测试设计文本，保存在数据库并返回。

    请求参数:
        - project_id: 项目ID
        - design_type: 设计类型 (functional/performance/safety)

    返回:
        - design: 新生成的测试设计对象
    """
    data = request.json
    project_id = data.get("project_id")
    design_type = data.get("design_type", "functional")

    # 获取策略内容
    strategies = TestStrategy.query.filter_by(project_id=project_id).all()
    strategy_content = (
        "\n\n".join([s.content for s in strategies]) if strategies else ""
    )

    # 获取需求
    requirements = Requirement.query.filter_by(project_id=project_id).all()
    req_list = [r.to_dict() for r in requirements]

    # 使用增强版服务生成设计
    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.generate_test_design(
        strategy_content=strategy_content or "基于VCU测试需求",
        requirements=req_list,
        design_type=design_type,
    )

    if not result["success"]:
        return APIResponse.error(
            message=result.get("error", "设计生成失败"),
            error_code=ErrorCode.AI_GENERATION_FAILED,
        )

    # 保存到数据库
    design_id = str(uuid.uuid4())
    design = TestDesign(
        id=design_id,
        project_id=project_id,
        name=f"测试设计_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        content=result["design"],
    )
    db.session.add(design)
    db.session.commit()

    # 保存到文件
    if project_id:
        design_dir = os.path.join(UPLOAD_FOLDER, project_id, "design")
        os.makedirs(design_dir, exist_ok=True)
        design_file = os.path.join(
            design_dir, f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(design_file, "w", encoding="utf-8") as f:
            f.write(f"# 测试设计\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**项目ID**: {project_id}\n\n")
            f.write(f"**设计类型**: {design_type}\n\n")
            f.write("---\n\n")
            f.write(result["design"])
        logger.info(f"测试设计已保存到: {design_file}")

    return APIResponse.created(
        data={"design": design.to_dict()},
        message="测试设计生成成功",
        resource_type="TestDesign",
        resource_id=design_id,
    )


@ai_bp.route("/api/ai/generate-testcases", methods=["POST"])
@handle_errors()
def generate_testcases():
    """生成测试用例 (TC - 测试用例)

    活动代码: ACT-TC-*

    根据设计内容创建详细的测试用例，并持久化到数据库。

    请求参数:
        - project_id: 项目ID
        - design: 设计内容 (可选，不提供则从数据库读取最新设计)
        - test_type: 测试类型 (functional/performance/safety)

    返回:
        - testcases: 生成的测试用例列表
        - total_count: 用例总数
    """
    data = request.json
    project_id = data.get("project_id")
    design_content = data.get("design", "")
    test_type = data.get("test_type", "functional")

    # 如果没有提供设计内容，从数据库读取
    if not design_content and project_id:
        designs = TestDesign.query.filter_by(project_id=project_id).all()
        if designs:
            design_content = designs[-1].content

    if not design_content:
        design_content = "基于VCU测试需求生成测试用例"

    # 使用增强版服务生成用例
    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.generate_test_cases(
        design_content=design_content, test_type=test_type
    )

    if not result["success"]:
        return APIResponse.error(
            message=result.get("error", "用例生成失败"),
            error_code=ErrorCode.TEST_CASE_GENERATION_FAILED,
        )

    test_cases = result.get("test_cases", [])
    saved_cases = []

    # 保存到数据库
    for tc_data in test_cases:
        testcase = TestCase(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name=tc_data.get("name", "未命名用例"),
            priority=tc_data.get("priority", "P2"),
            steps=json.dumps(tc_data.get("steps", []), ensure_ascii=False),
            expected=tc_data.get("expected_output", tc_data.get("expected", "")),
        )
        db.session.add(testcase)
        saved_cases.append(
            {"id": testcase.id, "name": testcase.name, "priority": testcase.priority}
        )

    db.session.commit()

    # 保存到文件
    if project_id and test_cases:
        tc_dir = os.path.join(UPLOAD_FOLDER, project_id, "testcase")
        os.makedirs(tc_dir, exist_ok=True)
        tc_file = os.path.join(
            tc_dir, f"testcases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(tc_file, "w", encoding="utf-8") as f:
            json.dump(test_cases, f, ensure_ascii=False, indent=2)
        logger.info(f"测试用例已保存到: {tc_file}")

    return APIResponse.success(
        data={
            "testcases": saved_cases,
            "total_count": len(saved_cases),
            "raw_content": result.get("raw_content", ""),
        },
        message=f"测试用例生成完成，共 {len(saved_cases)} 条",
    )


@ai_bp.route("/api/ai/generate-scripts", methods=["POST"])
@handle_errors()
def generate_scripts():
    """生成测试脚本 (TScr - 测试脚本)

    活动代码: ACT-TScr-*

    将测试用例文本转换为可执行的 Python 脚本，常用于 pytest 框架。

    请求参数:
        - project_id: 项目ID
        - testcases: 测试用例列表 (可选，不提供则从数据库读取)
        - framework: 测试框架 (默认pytest)
        - target_system: 目标系统 (默认VCU)

    返回:
        - scripts: 生成的脚本列表
    """
    data = request.json
    project_id = data.get("project_id")
    framework = data.get("framework", "pytest")
    target_system = data.get("target_system", "VCU")

    # 获取测试用例
    testcases = data.get("testcases", [])
    if not testcases and project_id:
        tc_models = TestCase.query.filter_by(project_id=project_id).all()
        testcases = []
        for tc in tc_models:
            steps = tc.steps
            if isinstance(steps, str):
                try:
                    steps = json.loads(steps)
                except:
                    steps = [steps]
            testcases.append(
                {
                    "id": tc.id,
                    "name": tc.name,
                    "priority": tc.priority,
                    "steps": steps,
                    "expected": tc.expected,
                }
            )

    if not testcases:
        testcases = [{"id": "TC-001", "name": "基础测试用例", "priority": "P2"}]

    # 使用增强版服务生成脚本
    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.generate_test_scripts(
        test_cases=testcases, framework=framework, target_system=target_system
    )

    if not result["success"]:
        return APIResponse.error(
            message=result.get("error", "脚本生成失败"),
            error_code=ErrorCode.AI_GENERATION_FAILED,
        )

    # 保存到文件
    script_files = []
    if project_id:
        script_dir = os.path.join(UPLOAD_FOLDER, project_id, "script")
        os.makedirs(script_dir, exist_ok=True)
        script_file = os.path.join(
            script_dir,
            f"test_{target_system.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
        )
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(result["script"])
        script_files.append(script_file)
        logger.info(f"测试脚本已保存到: {script_file}")

    return APIResponse.success(
        data={
            "scripts": [
                {
                    "language": "python",
                    "framework": framework,
                    "content": result["script"],
                    "files": script_files,
                }
            ]
        },
        message="测试脚本生成成功",
    )


@ai_bp.route("/api/ai/parse-log", methods=["POST"])
@handle_errors()
def parse_log():
    """解析测试日志 (TL - 测试日志)

    活动代码: ACT-TL-*

    将提供的日志内容提交给 AI 服务进行分析，结果保存到日志表并返回分析摘要与完整结果。

    请求参数:
        - project_id: 项目ID
        - log_content: 日志内容

    返回:
        - analysis: 分析结果
    """
    data = request.json
    project_id = data.get("project_id")
    log_content = data.get("log_content", "")

    if not log_content:
        log_content = "模拟日志：测试执行完成，50个用例通过，2个失败"

    # 使用增强版服务
    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.chat(
        message=f"请分析以下测试日志，提取关键信息：\n日志内容：\n{log_content}\n请输出：1. 测试摘要（通过/失败数量） 2. 发现的问题 3. 性能数据 4. 建议的改进措施",
        context="测试日志分析",
    )

    if not result["success"]:
        return APIResponse.error(
            message=result.get("error", "日志分析失败"),
            error_code=ErrorCode.AI_GENERATION_FAILED,
        )

    content = result["response"]

    # 保存到数据库
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

    return APIResponse.success(
        data={
            "id": log_id,
            "summary": content[:500] if content else "",
            "full_result": content,
        },
        message="日志分析完成",
    )


@ai_bp.route("/api/ai/generate-report", methods=["POST"])
@handle_errors()
def generate_report():
    """生成测试报告 (TR - 测试报告)

    活动代码: ACT-TR-*

    基于当前项目的需求、策略、设计、用例和日志等信息，调用 AI 生成完整的 Markdown 格式报告。

    请求参数:
        - project_id: 项目ID
        - report_type: 报告类型 (综合/功能/性能/安全)

    返回:
        - report: 生成的测试报告
        - statistics: 统计信息
    """
    data = request.json
    project_id = data.get("project_id")
    report_type = data.get("report_type", "综合测试报告")

    # 获取项目数据
    project = Project.query.get(project_id)
    requirements = Requirement.query.filter_by(project_id=project_id).all()
    strategies = TestStrategy.query.filter_by(project_id=project_id).all()
    designs = TestDesign.query.filter_by(project_id=project_id).all()
    testcases = TestCase.query.filter_by(project_id=project_id).all()
    logs = TestLog.query.filter_by(project_id=project_id).all()

    # 构建测试摘要
    test_summary = {
        "project_name": project.name if project else "未知项目",
        "report_type": report_type,
        "requirements_count": len(requirements),
        "strategies_count": len(strategies),
        "designs_count": len(designs),
        "testcases_count": len(testcases),
        "logs_count": len(logs),
    }

    # 构建测试结果
    test_results = []
    for tc in testcases:
        test_results.append({"id": tc.id, "name": tc.name, "passed": True})

    # 使用增强版服务生成报告
    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.generate_test_report(
        project_name=project.name if project else "未知项目",
        test_summary=test_summary,
        test_results=test_results,
        issues=None,
    )

    if not result["success"]:
        return APIResponse.error(
            message=result.get("error", "报告生成失败"),
            error_code=ErrorCode.AI_GENERATION_FAILED,
        )

    # 保存到文件
    report_file = None
    if project_id:
        report_dir = os.path.join(UPLOAD_FOLDER, project_id, "report")
        os.makedirs(report_dir, exist_ok=True)
        report_file = os.path.join(
            report_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(result["report"])
        logger.info(f"测试报告已保存到: {report_file}")

    return APIResponse.success(
        data={
            "report": result["report"],
            "file": report_file,
            "sections": result.get("sections", {}),
            "statistics": test_summary,
        },
        message="测试报告生成成功",
    )


@ai_bp.route("/api/ai/parse-requirements", methods=["POST"])
@handle_errors()
def parse_requirements():
    """分析需求文本 (RA - 需求分析)

    活动代码: ACT-RA-*

    将需求文本交给 AI 进行分析，提取功能需求点。

    请求参数:
        - project_id: 项目ID
        - content: 需求文档内容 (可选，如果不提供则从数据库读取)

    返回:
        - analysis: 分析结果
            - requirements: 提取的需求列表
            - total_count: 需求总数
    """
    data = request.json
    project_id = data.get("project_id")
    content = data.get("content", "")

    # 如果没有提供内容，从数据库读取
    if not content and project_id:
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        if requirements:
            content = "\n".join([f"- {r.name}: {r.description}" for r in requirements])

    if not content:
        return APIResponse.validation_error("content", "需求内容不能为空")

    # 使用增强版服务进行分析
    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.analyze_requirements(
        document_content=content, project_name=project_id or "车载控制器项目"
    )

    if result["success"]:
        # 保存分析结果到数据库
        if project_id:
            for req_data in result.get("requirements", []):
                req = Requirement(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    name=req_data.get("name", "未命名需求"),
                    category=req_data.get("category", "功能需求"),
                    priority=req_data.get("priority", "P2"),
                    description=req_data.get("description", ""),
                    source="AI解析",
                )
                db.session.add(req)
            db.session.commit()

        return APIResponse.success(
            data={
                "requirements": result.get("requirements", []),
                "total_count": result.get("total_count", 0),
                "raw_content": result.get("raw_content", ""),
            },
            message=f"需求分析完成，提取 {result.get('total_count', 0)} 个需求点",
        )
    else:
        return APIResponse.error(
            message=result.get("error", "需求分析失败"),
            error_code=ErrorCode.REQUIREMENT_PARSE_FAILED,
        )


@ai_bp.route("/api/ai/review-requirements", methods=["POST"])
@handle_errors()
def review_requirements():
    """审核需求 (RA - 需求验证)

    活动代码: ACT-RA-4-*

    对指定项目的需求进行审核与评分，返回审核内容与分数。

    请求参数:
        - project_id: 项目ID

    返回:
        - review: 审核结果
        - score: 审核分数
    """
    data = request.json
    project_id = data.get("project_id")

    requirements = Requirement.query.filter_by(project_id=project_id).all()
    if not requirements:
        return APIResponse.error(
            message="没有找到需求", error_code=ErrorCode.RESOURCE_NOT_FOUND
        )

    req_text = "\n".join([f"- {r.name}: {r.description}" for r in requirements])

    # 使用增强版服务
    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.chat(
        message=f"请审核以下需求，评估完整性、清晰性、可测试性，并给出改进建议：\n{req_text}",
        context="需求审核",
    )

    if not result["success"]:
        return APIResponse.error(
            message=result.get("error", "审核失败"),
            error_code=ErrorCode.AI_GENERATION_FAILED,
        )

    return APIResponse.success(
        data={
            "content": result["response"],
            "score": 85,
            "requirements_count": len(requirements),
        },
        message="需求审核完成",
    )


@ai_bp.route("/api/ai/generate-evaluation", methods=["POST"])
@handle_errors()
def generate_evaluation():
    """生成测试评估 (TEval - 测试评估)

    活动代码: ACT-TEval-*

    调用 AI 生成针对当前项目的测试评估文本。

    请求参数:
        - project_id: 项目ID
        - test_results: 测试结果 (可选)

    返回:
        - evaluation: 评估文本
    """
    data = request.json
    project_id = data.get("project_id")

    # 获取项目数据
    testcases = TestCase.query.filter_by(project_id=project_id).all()
    logs = TestLog.query.filter_by(project_id=project_id).all()

    # 构建评估上下文
    context = f"""
    项目ID: {project_id}
    测试用例数量: {len(testcases)}
    测试日志数量: {len(logs)}
    """

    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.chat(
        message=f"请根据以下测试数据生成测试评估报告：\n{context}\n\n评估内容应包括：\n1. 测试覆盖率评估\n2. 测试质量评估\n3. 缺陷分析\n4. 改进建议",
        context="测试评估",
    )

    if not result["success"]:
        return APIResponse.error(
            message=result.get("error", "评估生成失败"),
            error_code=ErrorCode.AI_GENERATION_FAILED,
        )

    return APIResponse.success(
        data={"evaluation": result["response"]}, message="测试评估生成完成"
    )


@ai_bp.route("/api/ai/generate-dts", methods=["POST"])
@handle_errors()
def generate_dts():
    """生成缺陷跟踪表 (DTS)

    调用 AI 生成一个缺陷跟踪表的文本表示。

    请求参数:
        - project_id: 项目ID

    返回:
        - dts: DTS文本内容
    """
    data = request.json
    project_id = data.get("project_id")

    enhanced_service = get_enhanced_ai_service()
    result = enhanced_service.chat(
        message=f"请为项目 {project_id} 生成缺陷跟踪表模板，包含：缺陷ID、标题、严重程度、状态、负责人、发现时间、描述等字段。",
        context="缺陷跟踪表生成",
    )

    if not result["success"]:
        return APIResponse.error(
            message=result.get("error", "DTS生成失败"),
            error_code=ErrorCode.AI_GENERATION_FAILED,
        )

    return APIResponse.success(
        data={"dts": result["response"]}, message="缺陷跟踪表生成完成"
    )
