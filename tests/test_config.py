"""测试配置加载"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import config

print("=" * 60)
print("配置测试")
print("=" * 60)
print(f"API Key: {'已设置' if config.openai_api_key else '未设置'}")
if config.openai_api_key:
    print(f"API Key (前10位): {config.openai_api_key[:10]}...")
print(f"API Base: {config.openai_api_base}")
print(f"LLM Model: {config.llm_model}")
print(f"Embedding Model: {config.embedding_model}")
print("=" * 60)

if not config.openai_api_key:
    print("\n错误：未找到 OPENAI_API_KEY")
    print("请检查 env 或 .env 文件是否存在并包含正确的配置")
    sys.exit(1)
else:
    print("\n配置加载成功！")

