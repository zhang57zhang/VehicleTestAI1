# -*- coding: utf-8 -*-
"""
VehicleTestAI - 配置管理模块
集中管理所有配置项，支持环境变量覆盖
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class AIConfig:
    """AI服务配置"""
    provider: str = field(default_factory=lambda: os.getenv("AI_PROVIDER", "glm"))
    api_key: str = field(default_factory=lambda: os.getenv("GLM_API_KEY") or os.getenv("ZHIPUAI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("GLM_MODEL") or os.getenv("ZHIPUAI_MODEL", "glm-4.7"))
    base_url: str = field(default_factory=lambda: os.getenv("AI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("AI_MAX_TOKENS", "4096")))
    temperature: float = field(default_factory=lambda: float(os.getenv("AI_TEMPERATURE", "0.7")))
    timeout: int = field(default_factory=lambda: int(os.getenv("AI_TIMEOUT", "180")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("AI_MAX_RETRIES", "3")))
    
    def is_configured(self) -> bool:
        """检查AI是否已配置"""
        return bool(self.api_key)


@dataclass
class DatabaseConfig:
    """数据库配置"""
    uri: str = field(default_factory=lambda: os.getenv("DATABASE_URI", "sqlite:///data/vehicletestai.db"))
    echo: bool = field(default_factory=lambda: os.getenv("DB_ECHO", "false").lower() == "true")
    pool_size: int = field(default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "5")))
    

@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = field(default_factory=lambda: os.getenv("SERVER_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("SERVER_PORT", "5000")))
    debug: bool = field(default_factory=lambda: os.getenv("FLASK_DEBUG", "false").lower() == "true")
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))


@dataclass
class UploadConfig:
    """上传配置"""
    folder: str = field(default_factory=lambda: os.getenv("UPLOAD_FOLDER", "uploads"))
    max_size: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE", str(100 * 1024 * 1024))))  # 100MB
    allowed_extensions: set = field(default_factory=lambda: {
        '.txt', '.md', '.pdf', '.doc', '.docx', '.xlsx', '.xls',
        '.dbc', '.arxml', '.blf', '.asc', '.csv', '.mf4',
        '.py', '.json', '.xml'
    })


@dataclass
class LogConfig:
    """日志配置"""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", 
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    file: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE", None))


@dataclass
class AppConfig:
    """应用总配置"""
    ai: AIConfig = field(default_factory=AIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    upload: UploadConfig = field(default_factory=UploadConfig)
    log: LogConfig = field(default_factory=LogConfig)
    
    # 测试活动配置
    test_activities: Dict[str, Any] = field(default_factory=lambda: {
        "RA": {"name": "需求分析", "enabled": True},
        "TS": {"name": "测试策略", "enabled": True},
        "TD": {"name": "测试设计", "enabled": True},
        "TC": {"name": "测试用例", "enabled": True},
        "TScr": {"name": "测试脚本", "enabled": True},
        "TE": {"name": "测试执行", "enabled": True},
        "TL": {"name": "测试日志", "enabled": True},
        "TEval": {"name": "测试评估", "enabled": True},
        "TR": {"name": "测试报告", "enabled": True}
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "ai": {
                "provider": self.ai.provider,
                "model": self.ai.model,
                "configured": self.ai.is_configured(),
                "max_tokens": self.ai.max_tokens,
                "temperature": self.ai.temperature
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port
            },
            "upload": {
                "max_size_mb": self.upload.max_size // (1024 * 1024),
                "allowed_extensions": list(self.upload.allowed_extensions)
            },
            "test_activities": self.test_activities
        }


# 全局配置实例
config = AppConfig()


def get_config() -> AppConfig:
    """获取配置实例"""
    return config


def reload_config():
    """重新加载配置"""
    global config
    load_dotenv(override=True)
    config = AppConfig()
