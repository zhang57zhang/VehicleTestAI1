# -*- coding: utf-8 -*-
"""
VehicleTestAI - AI提示词模板系统
基于test_system文档规范，提供标准化的提示词模板
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class PromptTemplate:
    """提示词模板基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def build(self, **kwargs) -> str:
        """构建提示词"""
        raise NotImplementedError


class RequirementAnalysisPrompt(PromptTemplate):
    """需求分析提示词模板

    对应测试活动: RA (Requirement Analysis)
    活动代码: ACT-RA-*
    """

    SYSTEM_PROMPT = """你是一个专业的车载控制器测试工程师，专注于需求分析。
你需要根据提供的文档内容，提取和整理功能需求、性能需求、安全需求和接口需求。

输出要求:
1. 使用JSON格式输出
2. 每个需求包含: id, name, category, priority, description
3. category可选值: 功能需求, 性能需求, 安全需求, 接口需求
4. priority可选值: P0(关键), P1(重要), P2(一般), P3(低)
5. 描述需要清晰、具体、可测试"""

    def __init__(self):
        super().__init__(
            name="requirement_analysis", description="需求分析模板 - 提取功能点"
        )

    def build(
        self,
        document_content: str,
        project_name: str = "车载控制器项目",
        additional_context: str = "",
    ) -> str:
        """构建需求分析提示词

        Args:
            document_content: 需求文档内容
            project_name: 项目名称
            additional_context: 额外上下文

        Returns:
            完整的提示词
        """
        prompt = f"""# 需求分析任务

## 项目信息
- 项目名称: {project_name}
- 分析时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 文档内容
{document_content}

## 分析要求
请根据上述文档内容，提取功能需求点。每个需求点需要包含:
1. 唯一标识符 (格式: FP001, FP002...)
2. 功能名称 (简洁明了)
3. 分类 (功能需求/性能需求/安全需求/接口需求)
4. 优先级 (P0/P1/P2/P3)
5. 详细描述 (包含验收标准)

## 输出格式
请输出JSON格式:
```json
{{
  "summary": "需求分析摘要",
  "total_count": 数量,
  "functional_requirements": [
    {{
      "id": "FP001",
      "name": "功能名称",
      "category": "功能需求",
      "priority": "P1",
      "description": "详细描述",
      "acceptance_criteria": ["验收标准1", "验收标准2"]
    }}
  ],
  "performance_requirements": [...],
  "safety_requirements": [...],
  "interface_requirements": [...]
}}
```

{additional_context}
"""
        return prompt


class TestStrategyPrompt(PromptTemplate):
    """测试策略提示词模板

    对应测试活动: TS (Test Strategy)
    活动代码: ACT-TS-*
    """

    SYSTEM_PROMPT = """你是一个专业的车载控制器测试策略专家。
你需要根据需求分析结果，制定完整的测试策略文档。

输出要求:
1. 使用Markdown格式
2. 包含测试范围、测试方法、测试环境、风险评估
3. 遵循ISO 26262功能安全标准
4. 考虑HIL/SIL测试环境"""

    def __init__(self):
        super().__init__(
            name="test_strategy", description="测试策略模板 - 制定测试方案"
        )

    def build(
        self,
        requirements: List[Dict],
        project_name: str = "车载控制器项目",
        test_environment: str = "HIL",
        skills: List[str] = None,
    ) -> str:
        """构建测试策略提示词

        Args:
            requirements: 需求列表
            project_name: 项目名称
            test_environment: 测试环境类型
            skills: 使用的测试技能

        Returns:
            完整的提示词
        """
        req_text = self._format_requirements(requirements)
        skills_text = ", ".join(skills) if skills else "标准测试方法"

        prompt = f"""# 测试策略生成任务

## 项目信息
- 项目名称: {project_name}
- 测试环境: {test_environment}
- 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 需求概述
{req_text}

## 测试技能
{skills_text}

## 策略要求
请生成完整的测试策略文档，包含以下章节:

### 1. 测试范围定义 (ACT-TS-1-1)
- 测试对象范围
- 测试类型范围
- 测试环境范围

### 2. 测试级别规划 (ACT-TS-1-2)
- 单元测试级别
- 集成测试级别
- 系统测试级别
- 验收测试级别

### 3. 测试方法选择 (ACT-TS-2)
- 黑盒测试方法 (等价类划分、边界值分析、因果图)
- 白盒测试方法 (语句覆盖、分支覆盖、MC/DC覆盖)
- 专项测试方法 (故障注入、性能测试、通信协议测试)

### 4. 测试环境策略 (ACT-TS-3)
- HIL环境配置策略
- SIL环境配置策略
- 实车测试策略

### 5. 资源配置 (ACT-TS-1-3)
- 人力资源
- 测试设备资源
- 工具资源

### 6. 风险评估
- 风险识别
- 风险等级
- 应对措施

请使用Markdown格式输出完整的测试策略文档。
"""
        return prompt

    def _format_requirements(self, requirements: List[Dict]) -> str:
        """格式化需求列表"""
        if not requirements:
            return "暂无需求信息"

        lines = []
        for req in requirements[:20]:  # 限制数量避免过长
            priority = req.get("priority", "P2")
            name = req.get("name", "未命名需求")
            category = req.get("category", "功能需求")
            lines.append(f"- [{priority}] {name} ({category})")

        if len(requirements) > 20:
            lines.append(f"... 共 {len(requirements)} 个需求")

        return "\n".join(lines)


class TestDesignPrompt(PromptTemplate):
    """测试设计提示词模板

    对应测试活动: TD (Test Design)
    活动代码: ACT-TD-*
    """

    SYSTEM_PROMPT = """你是一个专业的车载控制器测试设计工程师。
你需要根据测试策略，设计具体的测试方案和测试条件。

输出要求:
1. 使用Markdown格式
2. 包含测试覆盖模型、测试条件、测试数据
3. 明确前置条件和预期结果"""

    def __init__(self):
        super().__init__(name="test_design", description="测试设计模板 - 设计测试方案")

    def build(
        self,
        strategy_content: str,
        requirements: List[Dict] = None,
        design_type: str = "functional",
    ) -> str:
        """构建测试设计提示词"""
        req_context = ""
        if requirements:
            req_context = f"\n## 关联需求\n{self._format_requirements(requirements)}"

        prompt = f"""# 测试设计任务

## 设计类型
{design_type}

## 测试策略
{strategy_content}
{req_context}

## 设计要求
请根据测试策略，设计详细的测试方案，包含:

### 1. 测试覆盖模型 (ACT-TD-1-1)
- 功能覆盖模型
- 数据流覆盖模型
- 接口覆盖模型
- 安全覆盖模型

### 2. 测试条件设计 (ACT-TD-1-2)
- 正常测试条件
- 边界测试条件
- 异常测试条件

### 3. 测试数据设计 (ACT-TD-1-3)
- 测试输入数据
- 测试输出数据
- 测试数据脚本

### 4. 测试环境设计 (ACT-TD-2)
- HIL环境配置
- 测试工具配置
- 信号接口配置

请使用Markdown格式输出完整的测试设计文档。
"""
        return prompt

    def _format_requirements(self, requirements: List[Dict]) -> str:
        lines = []
        for req in requirements[:10]:
            lines.append(
                f"- {req.get('name', '未命名')}: {req.get('description', '')[:100]}"
            )
        return "\n".join(lines)


class TestCasePrompt(PromptTemplate):
    """测试用例提示词模板

    对应测试活动: TC (Test Cases)
    活动代码: ACT-TC-*
    """

    SYSTEM_PROMPT = """你是一个专业的车载控制器测试用例设计工程师。
你需要根据测试设计，编写详细的测试用例。

输出要求:
1. 使用JSON格式输出
2. 每个用例包含完整的测试步骤和预期结果
3. 用例需要可执行、可验证"""

    def __init__(self):
        super().__init__(name="test_case", description="测试用例模板 - 编写测试用例")

    def build(
        self,
        design_content: str,
        test_type: str = "functional",
        priority_filter: str = None,
    ) -> str:
        """构建测试用例提示词"""
        prompt = f"""# 测试用例生成任务

## 测试类型
{test_type}

## 测试设计
{design_content}

## 用例要求
请根据测试设计，生成详细的测试用例。每个用例包含:

### 用例结构
- 用例ID (格式: TC-模块-序号, 如 TC-COMM-001)
- 用例名称
- 测试模块
- 优先级 (P0/P1/P2/P3)
- 前置条件
- 测试步骤 (详细步骤列表)
- 测试输入
- 预期输出
- 通过标准

### 用例类型覆盖
1. 功能测试用例 (ACT-TC-1-1)
   - 正常功能用例
   - 边界功能用例
   - 异常处理用例

2. 性能测试用例 (ACT-TC-1-2)
   - 响应时间用例
   - 负载能力用例

3. 安全测试用例 (ACT-TC-1-3)
   - 故障检测用例
   - 故障处理用例
   - 故障恢复用例

## 输出格式
```json
{{
  "test_cases": [
    {{
      "id": "TC-COMM-001",
      "name": "CAN通信心跳测试",
      "module": "通信模块",
      "priority": "P0",
      "type": "functional",
      "precondition": "CAN总线正常连接",
      "steps": [
        "1. 启动CANoe监控",
        "2. 连接VCU控制器",
        "3. 监控CAN总线心跳报文"
      ],
      "input": "正常工作状态",
      "expected_output": "每100ms收到一次心跳报文",
      "pass_criteria": "心跳周期误差<5%"
    }}
  ]
}}
```

请生成至少5个测试用例。
"""
        return prompt


class TestScriptPrompt(PromptTemplate):
    """测试脚本提示词模板

    对应测试活动: TScr (Test Scripts)
    活动代码: ACT-TScr-*
    """

    SYSTEM_PROMPT = """你是一个专业的车载控制器自动化测试工程师。
你需要根据测试用例，编写Python自动化测试脚本。

输出要求:
1. 使用pytest框架
2. 代码符合PEP8规范
3. 包含完整的注释和文档字符串"""

    def __init__(self):
        super().__init__(
            name="test_script", description="测试脚本模板 - 编写自动化脚本"
        )

    def build(
        self,
        test_cases: List[Dict],
        framework: str = "pytest",
        target_system: str = "VCU",
    ) -> str:
        """构建测试脚本提示词"""
        tc_text = self._format_test_cases(test_cases)

        prompt = f"""# 测试脚本生成任务

## 目标系统
{target_system}

## 测试框架
{framework}

## 测试用例
{tc_text}

## 脚本要求
请根据测试用例，生成Python自动化测试脚本，包含:

### 1. 脚本结构
```python
# -*- coding: utf-8 -*-
\"\"\"
{target_system}自动化测试脚本
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
\"\"\"

import pytest
import can  # python-can库
import time

class Test{target_system}:
    \"\"\"{target_system}测试类\"\"\"
    
    @pytest.fixture(autouse=True)
    def setup(self):
        \"\"\"测试前置\"\"\"
        pass
    
    def test_xxx(self):
        \"\"\"测试用例\"\"\"
        pass
```

### 2. 代码规范
- 使用类型注解
- 包含docstring
- 异常处理完善
- 日志记录清晰

### 3. 测试功能
- CAN消息发送/接收
- 信号解析
- 结果断言
- 日志记录

请生成完整的测试脚本代码。
"""
        return prompt

    def _format_test_cases(self, test_cases: List[Dict]) -> str:
        lines = []
        for tc in test_cases[:10]:
            lines.append(f"### {tc.get('id', 'TC-XXX')}: {tc.get('name', '未命名')}")
            lines.append(f"- 优先级: {tc.get('priority', 'P2')}")
            lines.append(f"- 前置条件: {tc.get('precondition', '无')}")
            lines.append(f"- 预期结果: {tc.get('expected_output', '无')}")
            lines.append("")
        return "\n".join(lines)


class TestReportPrompt(PromptTemplate):
    """测试报告提示词模板

    对应测试活动: TR (Test Reports)
    活动代码: ACT-TR-*
    """

    SYSTEM_PROMPT = """你是一个专业的车载控制器测试报告编写工程师。
你需要根据测试执行结果，编写完整的测试报告。

输出要求:
1. 使用Markdown格式
2. 包含测试概述、结果统计、问题分析、结论建议
3. 符合ISO 26262测试报告要求"""

    def __init__(self):
        super().__init__(name="test_report", description="测试报告模板 - 编写测试报告")

    def build(
        self,
        project_name: str,
        test_summary: Dict,
        test_results: List[Dict],
        issues: List[Dict] = None,
    ) -> str:
        """构建测试报告提示词"""
        summary_text = json.dumps(test_summary, ensure_ascii=False, indent=2)
        results_text = self._format_results(test_results)
        issues_text = self._format_issues(issues) if issues else "无问题记录"

        prompt = f"""# 测试报告生成任务

## 项目信息
- 项目名称: {project_name}
- 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 测试摘要
{summary_text}

## 测试结果
{results_text}

## 问题列表
{issues_text}

## 报告要求
请生成完整的测试报告，包含以下章节:

### 1. 测试概述 (ACT-TR-1-1)
- 测试目的
- 测试范围
- 测试环境

### 2. 测试结果统计 (ACT-TR-1-1)
- 用例执行统计
- 通过率统计
- 覆盖率统计

### 3. 问题分析 (ACT-TR-1-1)
- 问题列表
- 问题分类
- 影响分析

### 4. 测试结论 (ACT-TR-1-1)
- 总体评价
- 发布建议
- 风险提示

### 5. 改进建议
- 测试改进
- 质量改进

请使用Markdown格式输出完整的测试报告。
"""
        return prompt

    def _format_results(self, results: List[Dict]) -> str:
        lines = []
        for r in results[:20]:
            status = "✓" if r.get("passed") else "✗"
            lines.append(
                f"- [{status}] {r.get('id', 'TC-XXX')}: {r.get('name', '未命名')}"
            )
        return "\n".join(lines)

    def _format_issues(self, issues: List[Dict]) -> str:
        lines = []
        for issue in issues:
            lines.append(
                f"- [{issue.get('severity', '中')}] {issue.get('title', '未命名')}"
            )
            lines.append(f"  描述: {issue.get('description', '')}")
        return "\n".join(lines)


class TestLogAnalysisPrompt(PromptTemplate):
    """测试日志分析提示词模板

    对应测试活动: TL (Test Logs)
    活动代码: ACT-TL-*
    """

    SYSTEM_PROMPT = """你是一个专业的车载控制器测试日志分析工程师。
你需要分析测试执行日志，提取关键信息和问题。

输出要求:
1. 使用JSON格式输出结构化数据
2. 识别测试通过/失败情况
3. 提取DTC码和警告信息
4. 给出改进建议"""

    def __init__(self):
        super().__init__(
            name="test_log_analysis", description="测试日志分析模板 - 解析测试日志"
        )

    def build(self, log_content: str, dbc_info: Dict = None) -> str:
        """构建日志分析提示词"""
        dbc_context = ""
        if dbc_info:
            dbc_context = (
                f"\n## DBC信息\n{json.dumps(dbc_info, ensure_ascii=False, indent=2)}"
            )

        prompt = f"""# 测试日志分析任务

## 日志内容
{log_content[:8000]}
{dbc_context}

## 分析要求
请分析测试日志，提取以下信息:

### 1. 测试执行摘要 (ACT-TL-1-2)
- 测试开始/结束时间
- 总用例数
- 通过/失败数量
- 执行时长

### 2. DTC检测 (ACT-TL-1-3)
- 检测到的DTC码列表
- DTC描述
- 出现次数

### 3. 信号分析 (ACT-TL-3-1)
- 关键信号数据
- 异常信号
- 性能指标

### 4. 问题识别 (ACT-TL-1-3)
- 错误信息
- 警告信息
- 异常事件

### 5. 改进建议
- 测试改进建议
- 问题修复建议

## 输出格式
```json
{{
  "summary": {{
    "total_tests": 数量,
    "passed": 数量,
    "failed": 数量,
    "duration": "时长"
  }},
  "dtc_codes": [
    {{
      "code": "DTC码",
      "description": "描述",
      "count": 次数
    }}
  ],
  "signals": [
    {{
      "name": "信号名",
      "value": "值",
      "status": "正常/异常"
    }}
  ],
  "issues": [
    {{
      "type": "error/warning",
      "message": "问题描述",
      "timestamp": "时间戳"
    }}
  ],
  "recommendations": ["建议1", "建议2"]
}}
```
"""
        return prompt


class TestEvaluationPrompt(PromptTemplate):
    """测试评估提示词模板

    对应测试活动: TEval (Test Evaluation)
    活动代码: ACT-TEval-*
    """

    SYSTEM_PROMPT = """你是一个专业的车载控制器测试评估工程师。
你需要根据测试结果，进行全面的测试评估。

输出要求:
1. 使用Markdown格式
2. 包含覆盖率评估、质量评估、效率评估
3. 给出量化指标和改进建议"""

    def __init__(self):
        super().__init__(
            name="test_evaluation", description="测试评估模板 - 评估测试质量"
        )

    def build(
        self,
        project_name: str,
        test_results: Dict,
        coverage_data: Dict = None,
        metrics: Dict = None,
    ) -> str:
        """构建测试评估提示词"""
        results_text = json.dumps(test_results, ensure_ascii=False, indent=2)
        coverage_text = (
            json.dumps(coverage_data, ensure_ascii=False, indent=2)
            if coverage_data
            else "暂无覆盖率数据"
        )
        metrics_text = (
            json.dumps(metrics, ensure_ascii=False, indent=2)
            if metrics
            else "暂无指标数据"
        )

        prompt = f"""# 测试评估任务

## 项目信息
- 项目名称: {project_name}
- 评估时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 测试结果
{results_text}

## 覆盖率数据
{coverage_text}

## 测试指标
{metrics_text}

## 评估要求
请进行全面的测试评估，包含以下内容:

### 1. 测试结果判定 (ACT-TEval-1-1)
- 实测与预期结果对比
- 通过/失败判定
- 不确定项分析

### 2. 缺陷分析 (ACT-TEval-1-2)
- 缺陷根因分析
- 缺陷影响评估
- 缺陷分类统计

### 3. 覆盖率评估 (ACT-TEval-2)
- 需求覆盖率统计
- 用例执行率统计
- 覆盖缺口分析

### 4. 质量评估
- 测试质量评分
- 测试效率评估
- 风险评估

### 5. 改进建议 (ACT-TEval-3-1)
- 测试改进建议
- 质量改进建议
- 后续测试建议

请使用Markdown格式输出完整的测试评估报告。
"""
        return prompt


class PromptTemplateManager:
    """提示词模板管理器"""

    def __init__(self):
        self.templates = {
            "requirement_analysis": RequirementAnalysisPrompt(),
            "test_strategy": TestStrategyPrompt(),
            "test_design": TestDesignPrompt(),
            "test_case": TestCasePrompt(),
            "test_script": TestScriptPrompt(),
            "test_log_analysis": TestLogAnalysisPrompt(),
            "test_evaluation": TestEvaluationPrompt(),
            "test_report": TestReportPrompt(),
        }

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates.get(name)

    def get_system_prompt(self, name: str) -> str:
        """获取系统提示词"""
        template = self.get_template(name)
        if template:
            return template.SYSTEM_PROMPT
        return "你是一个专业的车载控制器测试工程师。"

    def build_prompt(self, name: str, **kwargs) -> str:
        """构建提示词"""
        template = self.get_template(name)
        if template:
            return template.build(**kwargs)
        raise ValueError(f"未找到模板: {name}")

    def list_templates(self) -> List[Dict]:
        """列出所有模板"""
        return [
            {"name": name, "description": tmpl.description}
            for name, tmpl in self.templates.items()
        ]


# 全局模板管理器实例
prompt_manager = PromptTemplateManager()
