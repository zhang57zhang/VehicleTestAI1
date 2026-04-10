# -*- coding: utf-8 -*-
"""
VehicleTestAI - 增强版AI服务
集成模板系统、错误重试、响应解析
"""

import json
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from services.ai_service import AIServiceBase, GLMService, MockAIService, get_configured_ai_service
from services.prompt_templates import prompt_manager, PromptTemplate
from utils.error_handler import logger


class AIResponseParser:
    """AI响应解析器"""
    
    @staticmethod
    def extract_json(content: str) -> Optional[Dict]:
        """从响应中提取JSON
        
        Args:
            content: AI响应内容
            
        Returns:
            解析后的JSON字典，如果失败返回None
        """
        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取JSON代码块
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    @staticmethod
    def extract_markdown_sections(content: str) -> Dict[str, str]:
        """提取Markdown章节
        
        Args:
            content: Markdown内容
            
        Returns:
            章节字典 {标题: 内容}
        """
        sections = {}
        current_title = "header"
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_content:
                    sections[current_title] = '\n'.join(current_content).strip()
                current_title = line[3:].strip()
                current_content = []
            elif line.startswith('# '):
                if current_content:
                    sections[current_title] = '\n'.join(current_content).strip()
                current_title = line[2:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_title] = '\n'.join(current_content).strip()
        
        return sections
    
    @staticmethod
    def parse_requirements(content: str) -> List[Dict]:
        """解析需求分析结果
        
        Args:
            content: AI响应内容
            
        Returns:
            需求列表
        """
        # 尝试JSON解析
        json_result = AIResponseParser.extract_json(content)
        if json_result:
            requirements = []
            
            # 合并各类需求
            for key in ['functional_requirements', 'performance_requirements', 
                       'safety_requirements', 'interface_requirements']:
                if key in json_result and isinstance(json_result[key], list):
                    requirements.extend(json_result[key])
            
            if requirements:
                return requirements
        
        # 尝试文本解析
        requirements = []
        pattern = r'(FP\d+)[:：\s]*(.+?)(?=\n|$)'
        matches = re.findall(pattern, content)
        
        for i, (fp_id, name) in enumerate(matches):
            requirements.append({
                'id': fp_id,
                'name': name.strip(),
                'category': '功能需求',
                'priority': 'P2',
                'description': name.strip(),
                'source': 'AI解析'
            })
        
        return requirements
    
    @staticmethod
    def parse_test_cases(content: str) -> List[Dict]:
        """解析测试用例
        
        Args:
            content: AI响应内容
            
        Returns:
            测试用例列表
        """
        # 尝试JSON解析
        json_result = AIResponseParser.extract_json(content)
        if json_result and 'test_cases' in json_result:
            return json_result['test_cases']
        if isinstance(json_result, list):
            return json_result
        
        # 尝试文本解析
        test_cases = []
        pattern = r'(TC-\w+-\d+)[:：\s]*(.+?)(?=\n|TC-|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for tc_id, tc_content in matches:
            test_cases.append({
                'id': tc_id,
                'name': tc_content.strip().split('\n')[0][:100],
                'module': '通用',
                'priority': 'P2',
                'steps': [],
                'expected': ''
            })
        
        return test_cases


class EnhancedAIService:
    """增强版AI服务
    
    特性:
    - 集成模板系统
    - 自动重试机制
    - 响应解析
    - 结构化输出
    """
    
    def __init__(self, ai_service: AIServiceBase = None):
        self.ai_service = ai_service or get_configured_ai_service()
        self.max_retries = 3
        self.retry_delay = 2  # 秒
    
    def generate_with_retry(
        self,
        prompt: str,
        max_tokens: int = 4096,
        system_prompt: str = None
    ) -> Tuple[bool, str]:
        """带重试的生成
        
        Args:
            prompt: 提示词
            max_tokens: 最大token数
            system_prompt: 系统提示词
            
        Returns:
            (成功标志, 内容或错误消息)
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if hasattr(self.ai_service, 'client') and self.ai_service.client:
                    # GLM服务
                    response = self.ai_service.client.chat.completions.create(
                        model=self.ai_service.model,
                        messages=[
                            {"role": "system", "content": system_prompt or "你是一个专业的车载控制器测试工程师。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=max_tokens
                    )
                    content = response.choices[0].message.content
                else:
                    # Mock或其他服务
                    content = self.ai_service.generate(prompt, max_tokens)
                
                return True, content
                
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"AI生成失败，尝试 {attempt + 1}/{self.max_retries}",
                    error=last_error
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        
        return False, f"AI服务调用失败: {last_error}"
    
    def analyze_requirements(
        self,
        document_content: str,
        project_name: str = "车载控制器项目"
    ) -> Dict:
        """分析需求文档
        
        Args:
            document_content: 文档内容
            project_name: 项目名称
            
        Returns:
            分析结果
        """
        # 获取模板
        template = prompt_manager.get_template("requirement_analysis")
        
        # 构建提示词
        prompt = template.build(
            document_content=document_content,
            project_name=project_name
        )
        
        # 调用AI
        success, content = self.generate_with_retry(
            prompt=prompt,
            system_prompt=template.SYSTEM_PROMPT
        )
        
        if not success:
            return {
                "success": False,
                "error": content,
                "requirements": []
            }
        
        # 解析结果
        requirements = AIResponseParser.parse_requirements(content)
        
        return {
            "success": True,
            "raw_content": content,
            "requirements": requirements,
            "total_count": len(requirements),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def generate_test_strategy(
        self,
        requirements: List[Dict],
        project_name: str = "车载控制器项目",
        test_environment: str = "HIL",
        skills: List[str] = None
    ) -> Dict:
        """生成测试策略
        
        Args:
            requirements: 需求列表
            project_name: 项目名称
            test_environment: 测试环境
            skills: 测试技能列表
            
        Returns:
            测试策略结果
        """
        template = prompt_manager.get_template("test_strategy")
        
        prompt = template.build(
            requirements=requirements,
            project_name=project_name,
            test_environment=test_environment,
            skills=skills
        )
        
        success, content = self.generate_with_retry(
            prompt=prompt,
            system_prompt=template.SYSTEM_PROMPT
        )
        
        if not success:
            return {
                "success": False,
                "error": content,
                "strategy": None
            }
        
        return {
            "success": True,
            "strategy": content,
            "sections": AIResponseParser.extract_markdown_sections(content),
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_test_design(
        self,
        strategy_content: str,
        requirements: List[Dict] = None,
        design_type: str = "functional"
    ) -> Dict:
        """生成测试设计
        
        Args:
            strategy_content: 策略内容
            requirements: 需求列表
            design_type: 设计类型
            
        Returns:
            测试设计结果
        """
        template = prompt_manager.get_template("test_design")
        
        prompt = template.build(
            strategy_content=strategy_content,
            requirements=requirements,
            design_type=design_type
        )
        
        success, content = self.generate_with_retry(
            prompt=prompt,
            system_prompt=template.SYSTEM_PROMPT
        )
        
        if not success:
            return {
                "success": False,
                "error": content,
                "design": None
            }
        
        return {
            "success": True,
            "design": content,
            "sections": AIResponseParser.extract_markdown_sections(content),
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_test_cases(
        self,
        design_content: str,
        test_type: str = "functional"
    ) -> Dict:
        """生成测试用例
        
        Args:
            design_content: 设计内容
            test_type: 测试类型
            
        Returns:
            测试用例结果
        """
        template = prompt_manager.get_template("test_case")
        
        prompt = template.build(
            design_content=design_content,
            test_type=test_type
        )
        
        success, content = self.generate_with_retry(
            prompt=prompt,
            system_prompt=template.SYSTEM_PROMPT
        )
        
        if not success:
            return {
                "success": False,
                "error": content,
                "test_cases": []
            }
        
        test_cases = AIResponseParser.parse_test_cases(content)
        
        return {
            "success": True,
            "raw_content": content,
            "test_cases": test_cases,
            "total_count": len(test_cases),
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_test_scripts(
        self,
        test_cases: List[Dict],
        framework: str = "pytest",
        target_system: str = "VCU"
    ) -> Dict:
        """生成测试脚本
        
        Args:
            test_cases: 测试用例列表
            framework: 测试框架
            target_system: 目标系统
            
        Returns:
            测试脚本结果
        """
        template = prompt_manager.get_template("test_script")
        
        prompt = template.build(
            test_cases=test_cases,
            framework=framework,
            target_system=target_system
        )
        
        success, content = self.generate_with_retry(
            prompt=prompt,
            system_prompt=template.SYSTEM_PROMPT
        )
        
        if not success:
            return {
                "success": False,
                "error": content,
                "script": None
            }
        
        return {
            "success": True,
            "script": content,
            "language": "python",
            "framework": framework,
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_test_report(
        self,
        project_name: str,
        test_summary: Dict,
        test_results: List[Dict],
        issues: List[Dict] = None
    ) -> Dict:
        """生成测试报告
        
        Args:
            project_name: 项目名称
            test_summary: 测试摘要
            test_results: 测试结果
            issues: 问题列表
            
        Returns:
            测试报告结果
        """
        template = prompt_manager.get_template("test_report")
        
        prompt = template.build(
            project_name=project_name,
            test_summary=test_summary,
            test_results=test_results,
            issues=issues
        )
        
        success, content = self.generate_with_retry(
            prompt=prompt,
            system_prompt=template.SYSTEM_PROMPT
        )
        
        if not success:
            return {
                "success": False,
                "error": content,
                "report": None
            }
        
        return {
            "success": True,
            "report": content,
            "sections": AIResponseParser.extract_markdown_sections(content),
            "generated_at": datetime.now().isoformat()
        }
    
    def chat(
        self,
        message: str,
        history: List[Dict] = None,
        context: str = None
    ) -> Dict:
        """AI对话
        
        Args:
            message: 用户消息
            history: 对话历史
            context: 上下文
            
        Returns:
            对话响应
        """
        system_prompt = """你是一个专业的车载控制器测试AI助手。
你可以帮助工程师进行:
- 需求分析 (RA)
- 测试策略制定 (TS)
- 测试设计 (TD)
- 测试用例编写 (TC)
- 测试脚本生成 (TScr)
- 测试日志分析 (TL)
- 测试评估 (TEval)
- 测试报告生成 (TR)

请根据用户的问题提供专业、准确的回答，用中文回答。"""
        
        # 构建完整提示词
        full_prompt = ""
        if context:
            full_prompt += f"上下文信息:\n{context}\n\n"
        
        if history:
            for h in history[-10:]:  # 限制历史长度
                role = "用户" if h.get("role") == "user" else "助手"
                full_prompt += f"{role}: {h.get('content', '')}\n"
            full_prompt += "\n"
        
        full_prompt += f"用户: {message}\n\n请回答:"
        
        success, content = self.generate_with_retry(
            prompt=full_prompt,
            system_prompt=system_prompt
        )
        
        return {
            "success": success,
            "response": content if success else None,
            "error": None if success else content,
            "timestamp": datetime.now().isoformat()
        }


# 全局增强服务实例
_enhanced_service = None

def get_enhanced_ai_service() -> EnhancedAIService:
    """获取增强版AI服务实例"""
    global _enhanced_service
    if _enhanced_service is None:
        _enhanced_service = EnhancedAIService()
    return _enhanced_service
