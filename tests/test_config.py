"""测试配置 - 统一管理测试环境的警告和日志设置"""
import warnings
import os
import sys

# 抑制Pydantic弃用警告
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*dict.*method is deprecated.*')
warnings.filterwarnings('ignore', message='.*model_dump.*')

# 设置Windows控制台编码为UTF-8（避免日志中出现UnicodeEncodeError）
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
