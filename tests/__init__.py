"""测试模块初始化 - 统一设置警告过滤"""
import warnings
import os
import sys

# 在导入任何模块之前抑制所有Pydantic和LangChain相关警告
# 使用更全面的警告过滤策略
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*dict.*method is deprecated.*')
warnings.filterwarnings('ignore', message='.*model_dump.*')
warnings.filterwarnings('ignore', message='.*PydanticDeprecatedSince20.*')
warnings.filterwarnings('ignore', message='.*The `dict` method is deprecated.*')
warnings.filterwarnings('ignore', message='.*is deprecated.*')
# 抑制所有来自pydantic模块的警告
warnings.filterwarnings('ignore', module='pydantic.*')

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    try:
        import io
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass