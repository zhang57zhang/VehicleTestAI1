"""
日志分析服务
支持BLF、ASC、CSV等格式的CAN日志解析
使用DBC定义提取信号值并与测试用例匹配
"""

import os
import json
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple


class LogAnalysisService:
    """日志分析服务"""
    
    def __init__(self, dbc_service=None):
        self.dbc_service = dbc_service
        
    def parse_log_file(self, log_content: str, log_format: str = "blf") -> Dict[str, Any]:
        """
        解析日志文件
        
        Args:
            log_content: 日志文件内容
            log_format: 日志格式 (blf, asc, csv, mf4)
            
        Returns:
            解析结果
        """
        try:
            if log_format.lower() == "blf":
                return self._parse_blf(log_content)
            elif log_format.lower() == "asc":
                return self._parse_asc(log_content)
            elif log_format.lower() == "csv":
                return self._parse_csv(log_content)
            else:
                return self._parse_generic(log_content)
        except Exception as e:
            return {
                "success": False,
                "error": f"日志解析失败: {str(e)}",
                "messages": [],
                "signals": {}
            }
    
    def _parse_blf(self, content: str) -> Dict[str, Any]:
        """解析BLF格式日志"""
        try:
            import can
        except ImportError:
            return {
                "success": False,
                "error": "python-can库未安装，请运行: pip install python-can",
                "messages": [],
                "signals": {}
            }
        
        # BLF是二进制格式，这里简化处理
        # 实际应用中需要写入临时文件
        return {
            "success": True,
            "format": "blf",
            "messages": [],
            "signals": {},
            "note": "BLF格式需要二进制文件上传支持"
        }
    
    def _parse_asc(self, content: str) -> Dict[str, Any]:
        """解析ASC格式日志"""
        messages = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # ASC格式示例: 0.123456 1 1234#0102030405060708
            parts = line.split()
            if len(parts) >= 2:
                try:
                    timestamp = float(parts[0])
                    channel = parts[1]
                    
                    # 查找CAN ID和数据
                    if '#' in line:
                        id_data = line.split('#')[-1].split()
                        if len(id_data) >= 1:
                            can_id_str = id_data[0]
                            data_str = id_data[1] if len(id_data) > 1 else ""
                            
                            # 解析CAN ID
                            can_id = int(can_id_str, 16) if can_id_str.startswith(('0x', '0X')) else int(can_id_str)
                            
                            # 解析数据
                            data_bytes = bytes.fromhex(data_str.replace(' ', ''))
                            
                            messages.append({
                                "timestamp": timestamp,
                                "channel": channel,
                                "can_id": can_id,
                                "can_id_hex": hex(can_id),
                                "data": list(data_bytes),
                                "dlc": len(data_bytes)
                            })
                except (ValueError, IndexError):
                    continue
        
        return {
            "success": True,
            "format": "asc",
            "message_count": len(messages),
            "messages": messages,
            "signals": {}
        }
    
    def _parse_csv(self, content: str) -> Dict[str, Any]:
        """解析CSV格式日志"""
        import csv
        from io import StringIO
        
        messages = []
        signals = {}
        
        reader = csv.DictReader(StringIO(content))
        
        for row in reader:
            msg = {}
            for key, value in row.items():
                key_lower = key.lower().strip()
                
                # 尝试解析数值
                try:
                    if key_lower in ['timestamp', 'time']:
                        msg['timestamp'] = float(value)
                    elif key_lower in ['can_id', 'id', 'frame_id']:
                        msg['can_id'] = int(value, 16) if value.startswith('0x') else int(value)
                        msg['can_id_hex'] = hex(msg['can_id'])
                    elif key_lower in ['data', 'payload']:
                        msg['data'] = [int(b, 16) for b in value.split()]
                    elif key_lower == 'dlc':
                        msg['dlc'] = int(value)
                    else:
                        # 可能是信号值
                        try:
                            signals[key] = float(value)
                        except ValueError:
                            signals[key] = value
                except ValueError:
                    msg[key] = value
            
            if msg:
                messages.append(msg)
        
        return {
            "success": True,
            "format": "csv",
            "message_count": len(messages),
            "messages": messages,
            "signals": signals
        }
    
    def _parse_generic(self, content: str) -> Dict[str, Any]:
        """通用日志解析"""
        lines = content.strip().split('\n')
        
        return {
            "success": True,
            "format": "generic",
            "line_count": len(lines),
            "messages": [],
            "signals": {},
            "raw_content_preview": content[:500] if len(content) > 500 else content
        }
    
    def extract_signals_with_dbc(
        self, 
        log_messages: List[Dict], 
        dbc_name: str,
        dbc_cache: Dict
    ) -> Dict[str, Any]:
        """
        使用DBC定义从日志消息中提取信号值
        
        Args:
            log_messages: 日志消息列表
            dbc_name: DBC文件名
            dbc_cache: DBC缓存（包含db对象）
            
        Returns:
            提取的信号时序数据
        """
        if dbc_name not in dbc_cache:
            return {
                "success": False,
                "error": f"DBC {dbc_name} 未加载",
                "signals": {}
            }
        
        try:
            import cantools
            db = dbc_cache[dbc_name]["db"]
        except ImportError:
            return {
                "success": False,
                "error": "cantools库未安装",
                "signals": {}
            }
        
        extracted_signals = {}  # {signal_name: [(timestamp, value), ...]}
        
        for msg in log_messages:
            timestamp = msg.get("timestamp", 0)
            can_id = msg.get("can_id")
            data = msg.get("data", [])
            
            if can_id is None or not data:
                continue
            
            try:
                # 将数据转换为bytes
                data_bytes = bytes(data)
                
                # 使用DBC解码
                decoded = db.decode_message(can_id, data_bytes)
                
                for signal_name, value in decoded.items():
                    if signal_name not in extracted_signals:
                        extracted_signals[signal_name] = []
                    extracted_signals[signal_name].append({
                        "timestamp": timestamp,
                        "value": value
                    })
            except Exception:
                # 该消息ID不在DBC中，跳过
                continue
        
        # 计算信号统计信息
        signal_stats = {}
        for signal_name, values in extracted_signals.items():
            if values:
                numeric_values = [v["value"] for v in values if isinstance(v["value"], (int, float))]
                if numeric_values:
                    signal_stats[signal_name] = {
                        "count": len(values),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "avg": sum(numeric_values) / len(numeric_values),
                        "first": values[0],
                        "last": values[-1]
                    }
        
        return {
            "success": True,
            "signal_count": len(extracted_signals),
            "signals": extracted_signals,
            "signal_stats": signal_stats
        }
    
    def match_with_testcases(
        self,
        extracted_signals: Dict[str, List],
        testcases: List[Dict],
        tolerance: float = 0.05
    ) -> Dict[str, Any]:
        """
        将提取的信号与测试用例匹配
        
        Args:
            extracted_signals: 提取的信号数据 {signal_name: [(timestamp, value), ...]}
            testcases: 测试用例列表
            tolerance: 容差（百分比）
            
        Returns:
            匹配结果
        """
        results = []
        matched_count = 0
        mismatched_count = 0
        not_found_count = 0
        
        for tc in testcases:
            tc_id = tc.get("id", tc.get("tc_id", "unknown"))
            tc_name = tc.get("name", tc.get("tc_name", ""))
            
            # 从测试用例中提取期望信号
            # 假设测试用例有 expected_signals 字段或从 expected_result 解析
            expected_signals = tc.get("expected_signals", {})
            
            if not expected_signals:
                # 尝试从 expected_result 解析
                expected_result = tc.get("expected_result", "")
                if expected_result:
                    # 简单解析格式: "信号名: 期望值"
                    for line in expected_result.split('\n'):
                        if ':' in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                sig_name = parts[0].strip()
                                try:
                                    sig_value = float(parts[1].strip())
                                    expected_signals[sig_name] = sig_value
                                except ValueError:
                                    pass
            
            tc_result = {
                "testcase_id": tc_id,
                "testcase_name": tc_name,
                "signal_results": [],
                "status": "not_found"
            }
            
            if not expected_signals:
                tc_result["status"] = "no_expected_signals"
                results.append(tc_result)
                not_found_count += 1
                continue
            
            all_matched = True
            any_found = False
            
            for sig_name, expected_value in expected_signals.items():
                if sig_name in extracted_signals:
                    any_found = True
                    signal_data = extracted_signals[sig_name]
                    
                    # 获取信号值（取最后一个或平均值）
                    values = [v["value"] for v in signal_data if isinstance(v["value"], (int, float))]
                    
                    if values:
                        actual_value = values[-1]  # 取最后一个值
                        avg_value = sum(values) / len(values)
                        
                        # 计算误差
                        if expected_value != 0:
                            error_percent = abs(actual_value - expected_value) / abs(expected_value) * 100
                        else:
                            error_percent = abs(actual_value - expected_value) * 100
                        
                        matched = error_percent <= tolerance * 100
                        
                        tc_result["signal_results"].append({
                            "signal_name": sig_name,
                            "expected": expected_value,
                            "actual": actual_value,
                            "average": avg_value,
                            "error_percent": round(error_percent, 2),
                            "matched": matched,
                            "sample_count": len(values)
                        })
                        
                        if not matched:
                            all_matched = False
                    else:
                        tc_result["signal_results"].append({
                            "signal_name": sig_name,
                            "expected": expected_value,
                            "actual": None,
                            "matched": False,
                            "error": "无法获取数值"
                        })
                        all_matched = False
                else:
                    tc_result["signal_results"].append({
                        "signal_name": sig_name,
                        "expected": expected_value,
                        "actual": None,
                        "matched": False,
                        "error": "信号未在日志中找到"
                    })
                    all_matched = False
            
            if any_found:
                tc_result["status"] = "passed" if all_matched else "failed"
                if all_matched:
                    matched_count += 1
                else:
                    mismatched_count += 1
            else:
                tc_result["status"] = "signals_not_found"
                not_found_count += 1
            
            results.append(tc_result)
        
        return {
            "success": True,
            "total_testcases": len(testcases),
            "passed": matched_count,
            "failed": mismatched_count,
            "not_found": not_found_count,
            "pass_rate": round(matched_count / len(testcases) * 100, 2) if testcases else 0,
            "results": results,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def generate_analysis_report(
        self,
        log_info: Dict,
        dbc_info: Dict,
        signal_extraction: Dict,
        testcase_match: Dict
    ) -> str:
        """
        生成分析报告
        
        Args:
            log_info: 日志文件信息
            dbc_info: DBC解析信息
            signal_extraction: 信号提取结果
            testcase_match: 测试用例匹配结果
            
        Returns:
            Markdown格式的报告
        """
        report = f"""# CAN日志分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 日志文件信息

- **文件名**: {log_info.get('name', 'unknown')}
- **格式**: {log_info.get('format', 'unknown')}
- **消息数量**: {log_info.get('message_count', 0)}
- **错误帧**: {log_info.get('errors', 0)}
- **DTC数量**: {log_info.get('dtcs', 0)}

## 2. DBC解析信息

- **DBC文件**: {dbc_info.get('dbc_name', 'unknown')}
- **消息定义数**: {dbc_info.get('message_count', 0)}
- **信号定义数**: {dbc_info.get('signal_count', 0)}

## 3. 信号提取结果

共提取 **{signal_extraction.get('signal_count', 0)}** 个信号:

| 信号名 | 采样数 | 最小值 | 最大值 | 平均值 |
|--------|--------|--------|--------|--------|
"""
        
        for sig_name, stats in signal_extraction.get("signal_stats", {}).items():
            report += f"| {sig_name} | {stats['count']} | {stats['min']:.2f} | {stats['max']:.2f} | {stats['avg']:.2f} |\n"
        
        report += f"""
## 4. 测试用例匹配结果

- **总用例数**: {testcase_match.get('total_testcases', 0)}
- **通过**: {testcase_match.get('passed', 0)}
- **失败**: {testcase_match.get('failed', 0)}
- **未找到**: {testcase_match.get('not_found', 0)}
- **通过率**: {testcase_match.get('pass_rate', 0)}%

### 详细结果

| 用例ID | 用例名称 | 状态 | 匹配信号数 |
|--------|----------|------|------------|
"""
        
        for result in testcase_match.get("results", []):
            matched_signals = sum(1 for s in result.get("signal_results", []) if s.get("matched"))
            total_signals = len(result.get("signal_results", []))
            status_emoji = "✅" if result["status"] == "passed" else "❌" if result["status"] == "failed" else "⚠️"
            report += f"| {result['testcase_id']} | {result['testcase_name']} | {status_emoji} {result['status']} | {matched_signals}/{total_signals} |\n"
        
        report += """
## 5. 结论与建议

"""
        
        pass_rate = testcase_match.get('pass_rate', 0)
        if pass_rate >= 90:
            report += "✅ 测试结果良好，大部分测试用例通过。\n"
        elif pass_rate >= 70:
            report += "⚠️ 测试结果一般，建议检查失败的测试用例。\n"
        else:
            report += "❌ 测试结果较差，需要重点关注失败的测试用例。\n"
        
        # 添加失败用例的建议
        failed_cases = [r for r in testcase_match.get("results", []) if r["status"] == "failed"]
        if failed_cases:
            report += "\n### 失败用例分析\n\n"
            for fc in failed_cases[:5]:  # 最多显示5个
                report += f"**{fc['testcase_id']}**: {fc['testcase_name']}\n"
                for sr in fc.get("signal_results", []):
                    if not sr.get("matched"):
                        report += f"  - {sr['signal_name']}: 期望 {sr.get('expected')}，实际 {sr.get('actual')}\n"
                report += "\n"
        
        return report


# 全局日志分析服务实例
log_analysis_service = LogAnalysisService()
