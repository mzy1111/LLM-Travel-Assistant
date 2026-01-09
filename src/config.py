"""配置管理模块"""
import os
import yaml
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量（优先加载 .env，如果不存在则加载 env）
if not load_dotenv('.env'):
    load_dotenv('env')


class Config:
    """配置类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._load_config()
        self._load_env()
    
    def _load_config(self):
        """加载YAML配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}
    
    def _load_env(self):
        """加载环境变量"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.llm_model = os.getenv("LLM_MODEL", self.config.get("llm", {}).get("model", "gpt-4-turbo-preview"))
    
    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default


# 全局配置实例
config = Config()

