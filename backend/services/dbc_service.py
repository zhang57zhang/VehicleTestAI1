"""
DBC文件解析服务
使用cantools库解析DBC文件，提取CAN信号定义
"""

import os
import json
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any


class DBCService:
    """DBC文件解析服务"""

    def __init__(self):
        self.dbc_cache = {}  # 缓存已解析的DBC文件

    def parse_dbc_file(
        self, dbc_content: str, dbc_name: str = "unknown.dbc"
    ) -> Dict[str, Any]:
        """
        解析DBC文件内容

        Args:
            dbc_content: DBC文件内容字符串
            dbc_name: DBC文件名

        Returns:
            解析结果，包含messages和signals
        """
        try:
            import cantools
        except ImportError:
            return {
                "success": False,
                "error": "cantools库未安装，请运行: pip install cantools",
                "messages": [],
                "signals": [],
            }

        try:
            # 写入临时文件让cantools解析
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".dbc", delete=False, encoding="utf-8"
            ) as f:
                f.write(dbc_content)
                temp_path = f.name

            try:
                db = cantools.database.load_file(temp_path)

                messages = []
                signals = []

                for msg in db.messages:
                    msg_info = {
                        "name": msg.name,
                        "frame_id": hex(msg.frame_id),
                        "frame_id_int": msg.frame_id,
                        "length": msg.length,
                        "is_extended_frame": msg.is_extended_frame,
                        "comment": msg.comment or "",
                        "signals": [],
                    }

                    for sig in msg.signals:
                        sig_info = {
                            "name": sig.name,
                            "start_bit": sig.start,
                            "length": sig.length,
                            "byte_order": "little_endian"
                            if sig.byte_order == "little"
                            else "big_endian",
                            "is_signed": sig.is_signed,
                            "scale": float(sig.scale) if sig.scale else 1.0,
                            "offset": float(sig.offset) if sig.offset else 0.0,
                            "minimum": float(sig.minimum)
                            if sig.minimum is not None
                            else None,
                            "maximum": float(sig.maximum)
                            if sig.maximum is not None
                            else None,
                            "unit": sig.unit or "",
                            "comment": sig.comment or "",
                            "message_name": msg.name,
                        }
                        msg_info["signals"].append(sig_info)
                        signals.append(sig_info)

                    messages.append(msg_info)

                # 缓存解析结果
                cache_key = dbc_name
                self.dbc_cache[cache_key] = {
                    "db": db,
                    "messages": messages,
                    "signals": signals,
                }

                return {
                    "success": True,
                    "dbc_name": dbc_name,
                    "message_count": len(messages),
                    "signal_count": len(signals),
                    "messages": messages,
                    "signals": signals,
                    "parsed_at": datetime.now().isoformat(),
                }

            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            return {
                "success": False,
                "error": f"DBC解析失败: {str(e)}",
                "messages": [],
                "signals": [],
            }

    def decode_can_message(
        self, dbc_name: str, frame_id: int, data: bytes
    ) -> Optional[Dict[str, Any]]:
        """
        使用DBC定义解码CAN消息

        Args:
            dbc_name: DBC文件名（用于查找缓存）
            frame_id: CAN帧ID
            data: CAN数据字节

        Returns:
            解码后的信号字典
        """
        if dbc_name not in self.dbc_cache:
            return None

        try:
            db = self.dbc_cache[dbc_name]["db"]
            decoded = db.decode_message(frame_id, data)
            return decoded
        except Exception as e:
            return None

    def get_signal_definition(
        self, dbc_name: str, signal_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取信号定义

        Args:
            dbc_name: DBC文件名
            signal_name: 信号名

        Returns:
            信号定义字典
        """
        if dbc_name not in self.dbc_cache:
            return None

        for sig in self.dbc_cache[dbc_name]["signals"]:
            if sig["name"] == signal_name:
                return sig
        return None

    def get_message_by_frame_id(
        self, dbc_name: str, frame_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        根据帧ID获取消息定义

        Args:
            dbc_name: DBC文件名
            frame_id: CAN帧ID

        Returns:
            消息定义字典
        """
        if dbc_name not in self.dbc_cache:
            return None

        for msg in self.dbc_cache[dbc_name]["messages"]:
            if msg["frame_id_int"] == frame_id:
                return msg
        return None

    def list_available_signals(self, dbc_name: str) -> List[str]:
        """
        列出DBC中所有可用信号名

        Args:
            dbc_name: DBC文件名

        Returns:
            信号名列表
        """
        if dbc_name not in self.dbc_cache:
            return []
        return [sig["name"] for sig in self.dbc_cache[dbc_name]["signals"]]


# 全局DBC服务实例
dbc_service = DBCService()
