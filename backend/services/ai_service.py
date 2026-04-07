# -*- coding: utf-8 -*-
"""
车载控制器测试AI平台 - AI服务模块
提供AI生成逻辑，支持接入多种AI服务
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# ==================== AI服务基类 ====================


class AIServiceBase:
    """AI服务基类"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成内容 - 子类实现"""
        raise NotImplementedError

    def analyze(self, content: str) -> Dict:
        """分析内容 - 子类实现"""
        raise NotImplementedError


# ==================== 模拟AI服务 ====================


class MockAIService(AIServiceBase):
    """
    模拟AI服务 - 用于开发和测试
    返回结构化的测试相关文档
    """

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成模拟AI内容"""
        if "strategy" in prompt.lower() or "策略" in prompt:
            return self._generate_strategy()
        elif "design" in prompt.lower() or "设计" in prompt:
            return self._generate_design()
        elif "testcase" in prompt.lower() or "用例" in prompt:
            return self._generate_testcase()
        elif "script" in prompt.lower() or "脚本" in prompt:
            return self._generate_script()
        elif "report" in prompt.lower() or "报告" in prompt:
            return self._generate_report()
        elif "log" in prompt.lower() or "日志" in prompt:
            return self._generate_log_analysis()
        elif "requirement" in prompt.lower() or "需求" in prompt:
            return self._generate_requirement_analysis()
        else:
            return self._generate_generic()

    def _generate_strategy(self) -> str:
        """生成测试策略"""
        return f"""# 测试策略文档

## 1. 概述
本文档定义了车载控制器测试的完整策略，涵盖功能测试、性能测试、安全测试等方面。

## 2. 测试范围
- VCU通信协议测试
- 动力系统控制测试
- 底盘系统控制测试
- 传感器数据采集测试
- 故障诊断功能测试

## 3. 测试方法
| 测试类型 | 测试方法 | 测试工具 |
|----------|----------|----------|
| 功能测试 | 黑盒测试 | CANoe |
| 接口测试 | 灰盒测试 | pytest |
| 性能测试 | 负载测试 | JMeter |
| 安全测试 | 渗透测试 | 自定义工具 |

## 4. 测试环境
- 硬件：VCU控制器 x 1, HIL台架 x 1
- 软件：CANoe 14, pytest, Python 3.10+

## 5. 风险评估
| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 需求变更 | 中 | 高 | 敏捷迭代 |
| 环境问题 | 低 | 高 | 备选环境 |

生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def _generate_design(self) -> str:
        """生成测试设计"""
        return """# 测试设计文档

## 模块1：VCU通信测试设计

### 1.1 测试目标
验证VCU与其他ECU之间的CAN通信协议正确性。

### 1.2 测试用例
| 用例ID | 用例名称 | 输入 | 预期输出 |
|--------|----------|------|----------|
| TD-001 | 心跳测试 | 正常CAN帧 | 响应正确 |
| TD-002 | 多帧传输 | 长数据帧 | 正确分包重组 |
| TD-003 | 错误注入 | 错误CAN帧 | 错误处理正确 |

### 1.3 测试数据
- CAN ID: 0x100-0x1FF
- 数据长度: 0-64字节
- 周期: 10ms-1000ms

## 模块2：动力控制测试设计

### 2.1 测试目标
验证动力系统控制逻辑的正确性。

### 2.2 测试用例
| 用例ID | 用例名称 | 输入 | 预期输出 |
|--------|----------|------|----------|
| TD-010 | 加速响应 | 踏板开度0-100% | 扭矩响应线性 |
| TD-011 | 制动响应 | 制动信号 | 能量回收启动 |

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _generate_testcase(self) -> str:
        """生成测试用例"""
        return """# 测试用例文档

## TC-001: VCU心跳报文发送测试
- **模块**: 通信协议
- **优先级**: P0
- **前置条件**: CAN总线正常连接
- **测试步骤**:
  1. 启动CANoe监控
  2. 连接VCU控制器
  3. 监控CAN总线
- **预期结果**: 每100ms收到一次心跳报文

## TC-002: 加速踏板响应测试
- **模块**: 动力控制
- **优先级**: P0
- **前置条件**: 车辆处于READY状态
- **测试步骤**:
  1. 发送加速踏板信号(0%)
  2. 逐步增加踏板开度
  3. 记录扭矩响应
- **预期结果**: 扭矩随踏板开度线性增加

## TC-003: 故障码存储测试
- **模块**: 故障诊断
- **优先级**: P1
- **前置条件**: DTC功能使能
- **测试步骤**:
  1. 注入预设故障
  2. 等待500ms
  3. 读取DTC
- **预期结果**: 相应DTC被正确存储

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _generate_script(self) -> str:
        """生成测试脚本"""
        return '''# -*- coding: utf-8 -*-
"""
VCU测试脚本 - pytest框架
"""

import pytest
import can
import time


class VCUTester:
    """VCU测试器"""

    def __init__(self, channel=0):
        self.bus = can.interface.Bus(channel=channel, bustype='pcan')

    def send_can(self, can_id, data):
        """发送CAN消息"""
        msg = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=False
        )
        self.bus.send(msg)

    def recv_can(self, timeout=1.0):
        """接收CAN消息"""
        return self.bus.recv(timeout)


@pytest.fixture
def vcu():
    """VCU测试fixture"""
    tester = VCUTester()
    yield tester
    tester.bus.shutdown()


def test_heartbeat(vcu):
    """心跳测试"""
    vcu.send_can(0x100, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])
    msg = vcu.recv_can(timeout=0.2)
    assert msg is not None, "未收到心跳报文"


def test_accelerator(vcu):
    """加速踏板测试"""
    for pedal in range(0, 101, 25):
        signal = int(pedal * 2.55)
        vcu.send_can(0x300, [signal, 0, 0, 0, 0, 0, 0, 0])
        time.sleep(0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

    def _generate_report(self) -> str:
        """生成测试报告"""
        return f"""# 测试报告

## 1. 测试概述
| 项目 | 数值 |
|------|------|
| 测试用例总数 | 50 |
| 通过用例 | 48 |
| 失败用例 | 2 |
| 通过率 | 96% |

## 2. 测试执行情况
- 测试时间：2026-04-04 09:00 - 18:00
- 测试人员：张工、李工、王工
- 测试环境：HIL台架 + CANoe

## 3. 缺陷统计
| 严重程度 | 数量 | 状态 |
|----------|------|------|
| 严重 | 0 | 已关闭 |
| 主要 | 1 | 已修复 |
| 次要 | 3 | 已修复 |

## 4. 测试结论
本次测试覆盖了VCU的主要功能点，整体通过率96%，满足发布标准。建议后续继续完善边界条件测试。

---
报告生成：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def _generate_log_analysis(self) -> str:
        """生成日志分析"""
        return """# 日志解析结果

## 测试执行摘要
| 指标 | 数值 |
|------|------|
| 总测试数 | 50 |
| 通过 | 48 |
| 失败 | 2 |
| 错误 | 0 |

## DTC检测
| DTC码 | 描述 | 出现次数 |
|-------|------|----------|
| P0500 | 车速传感器故障 | 1 |
| C0030 | 左轮速传感器 | 2 |

## 警告信息
1. 通信延迟超过阈值
2. 传感器数据异常

## 建议
1. 检查车速传感器线路
2. 优化CAN总线负载

解析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _generate_requirement_analysis(self) -> str:
        """生成需求分析"""
        return """# 需求分析结果

## 功能需求
1. VCU应支持标准CAN通信协议
2. VCU应支持10ms-1000ms周期的心跳报文
3. VCU应支持故障诊断功能
4. VCU应支持扭矩控制功能

## 非功能需求
1. 响应时间 < 50ms
2. CAN总线负载 < 70%
3. 可靠性 > 99.9%

## 风险项
1. 需求变更风险
2. 第三方依赖风险

分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _generate_generic(self) -> str:
        """生成通用内容"""
        return f"""# AI生成内容

根据您的需求，已生成相关文档内容。

生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def analyze(self, content: str) -> Dict:
        """分析内容"""
        analysis = {
            "summary": "分析完成",
            "keywords": [],
            "requirements": [],
            "risks": [],
        }

        # 简单关键词提取
        keywords = ["CAN", "VCU", "扭矩", "故障", "诊断", "测试", "协议"]
        for kw in keywords:
            if kw in content:
                analysis["keywords"].append(kw)

        return analysis


# ==================== 智谱GLM AI服务 ====================


class GLMService(AIServiceBase):
    """
    智谱GLM AI服务
    支持GLM-4-Plus, GLM-4, GLM-3-Turbo, GLM-4.7, GLM-5等模型
    使用zhipuai库调用API
    """

    # 支持的模型列表（按优先级排序）
    SUPPORTED_MODELS = [
        "glm-4.7",
        "glm-4-plus",
        "glm-4",
        "glm-3-turbo",
        "glm-4-air",
        "glm-4-airx",
    ]

    def __init__(self, api_key: str = None, model: str = "glm-4.7"):
        super().__init__(api_key)
        self.model = model
        self.client = None
        self._model_validated = False

        # Initialize zhipuai client if api_key is provided
        if self.api_key:
            try:
                from zhipuai import ZhipuAI

                self.client = ZhipuAI(api_key=self.api_key)
                print(f"✅ 智谱AI客户端初始化成功，模型: {self.model}")
            except ImportError:
                print(
                    "Warning: zhipuai library not installed. Run: pip install zhipuai"
                )
                self.client = None

    def generate(self, prompt: str, max_tokens: int = 4096) -> str:
        """调用智谱GLM API生成内容，支持模型自动回退"""
        if not self.api_key or not self.client:
            # 没有API Key时使用模拟服务
            mock = MockAIService()
            return mock.generate(prompt, max_tokens)

        # 尝试模型列表（优先使用配置的模型）
        models_to_try = [self.model]
        for m in self.SUPPORTED_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的车载控制器测试工程师，专注于VCU测试文档生成。请用中文回答，输出格式化的Markdown文档或JSON格式。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.6,
                )

                # Get response content
                if response and hasattr(response, "choices") and len(response.choices) > 0:
                    if model != self.model:
                        print(f"⚠️ 模型 {self.model} 不可用，已回退到 {model}")
                    print(f"✅ GLM API 调用成功，模型: {model}")
                    return response.choices[0].message.content
                else:
                    last_error = "API返回异常: 无有效响应"
                    continue

            except Exception as e:
                error_msg = str(e)
                last_error = error_msg
                print(f"⚠️ 模型 {model} 调用失败: {error_msg[:100]}")
                
                # 如果是认证错误或API key错误，不需要尝试其他模型
                if "401" in error_msg or "403" in error_msg or "invalid" in error_msg.lower():
                    break
                continue

        # 所有模型都失败，回退到模拟服务
        print(f"❌ 所有模型尝试失败，回退到 Mock 服务")
        mock = MockAIService()
        return mock.generate(prompt, max_tokens)

    def analyze(self, content: str) -> Dict:
        """调用智谱GLM API分析内容"""
        prompt = f"请分析以下需求文档，提取功能需求、非功能需求和风险项：\n\n{content}"
        result = self.generate(prompt)
        return {
            "summary": result,
            "analyzed": True,
            "timestamp": datetime.now().isoformat(),
        }


# ==================== MiniMax AI服务 ====================


class MiniMaxService(AIServiceBase):
    """
    MiniMax AI服务
    需要配置 MINIMAX_API_KEY 环境变量
    """

    API_URL = "https://api.minimax.chat/v1/text/chatcompletion_pro"

    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.model = "abab5.5-chat"

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """调用MiniMax API生成内容"""
        if not self.api_key:
            # 没有API Key时使用模拟服务
            mock = MockAIService()
            return mock.generate(prompt, max_tokens)

        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的车载控制器测试工程师，专注于VCU测试文档生成。",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }

            response = requests.post(
                self.API_URL, headers=headers, json=data, timeout=30
            )
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"API返回异常: {result}"

        except Exception as e:
            # 失败时回退到模拟服务
            mock = MockAIService()
            return mock.generate(prompt, max_tokens)

    def analyze(self, content: str) -> Dict:
        """调用MiniMax API分析内容"""
        prompt = f"请分析以下需求文档，提取功能需求、非功能需求和风险项：\n\n{content}"
        result = self.generate(prompt)
        return {
            "summary": result,
            "analyzed": True,
            "timestamp": datetime.now().isoformat(),
        }


# ==================== 服务工厂 ====================


def get_ai_service(
    service_type: str = "mock", api_key: str = None, model: str = None
) -> AIServiceBase:
    """
    获取AI服务实例

    Args:
        service_type: 服务类型 ("mock", "glm", "minimax", "openai")
        api_key: API密钥
        model: 模型名称 (对于GLM: glm-4-plus, glm-4, glm-3-turbo)

    Returns:
        AIServiceBase: AI服务实例
    """
    services = {
        "mock": MockAIService,
        "glm": GLMService,
        "minimax": MiniMaxService,
    }

    service_class = services.get(service_type, MockAIService)

    if service_type == "glm":
        return service_class(api_key, model or "glm-4-plus")

    return service_class(api_key)


# ==================== 测试文档生成器 ====================


class TestDocumentGenerator:
    """测试文档生成器"""

    def __init__(self, ai_service: AIServiceBase = None):
        self.ai_service = ai_service or MockAIService()

    def generate_strategy(
        self, requirements: str, system_design: str = "", skills: List[str] = None
    ) -> str:
        """生成测试策略"""
        prompt = f"""请为车载控制器(VCU)测试生成测试策略文档。

需求内容：
{requirements}

系统设计：
{system_design}

使用的测试技能：{", ".join(skills) if skills else "标准测试"}

请包含以下内容：
1. 测试范围定义
2. 测试策略和方法
3. 测试环境要求
4. 测试进度安排
5. 风险评估和应对
"""
        return self.ai_service.generate(prompt)

    def generate_design(self, requirements: str, test_points: List[str] = None) -> str:
        """生成测试设计"""
        prompt = f"""请为车载控制器测试生成测试设计文档。

需求内容：
{requirements}

测试要点：
{chr(10).join(test_points) if test_points else "标准测试点"}

请包含以下内容：
1. 测试模块划分
2. 测试用例设计
3. 测试数据准备
4. 测试环境配置
"""
        return self.ai_service.generate(prompt)

    def generate_testcases(
        self, requirements: str, designs: List[str] = None
    ) -> List[Dict]:
        """生成测试用例"""
        prompt = f"""请为车载控制器测试生成详细的测试用例。

需求内容：
{requirements}

测试设计：
{chr(10).join(designs) if designs else "标准测试设计"}

请为每个用例包含：
- 用例ID
- 用例名称
- 测试模块
- 优先级
- 前置条件
- 测试步骤
- 预期结果
"""
        result = self.ai_service.generate(prompt)
        # 解析为结构化数据
        return self._parse_testcases(result)

    def _parse_testcases(self, content: str) -> List[Dict]:
        """解析测试用例"""
        testcases = []
        # 简单的正则解析
        import re

        # 查找用例
        pattern = r"TC-\d+[:：]?\s*(.+)"
        matches = re.findall(pattern, content)

        for i, match in enumerate(matches):
            testcases.append(
                {
                    "id": f"TC-{i + 1:03d}",
                    "name": match.strip() if match else f"测试用例{i + 1}",
                    "module": "通用模块",
                    "priority": "P1",
                    "steps": ["执行测试步骤"],
                    "expected": ["符合预期结果"],
                }
            )

        if not testcases:
            # 生成默认用例
            testcases = [
                {
                    "id": "TC-001",
                    "name": "VCU心跳测试",
                    "module": "通信",
                    "priority": "P0",
                    "steps": ["监控CAN"],
                    "expected": ["收到心跳"],
                },
                {
                    "id": "TC-002",
                    "name": "扭矩响应测试",
                    "module": "控制",
                    "priority": "P0",
                    "steps": ["发送扭矩请求"],
                    "expected": ["扭矩响应"],
                },
            ]

        return testcases


# ==================== 导出 ====================

__all__ = [
    "AIServiceBase",
    "MockAIService",
    "GLMService",
    "MiniMaxService",
    "get_ai_service",
    "TestDocumentGenerator",
]
