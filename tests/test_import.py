"""测试导入"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.config import config
    print("✓ config 导入成功")
    
    from src.agent.travel_agent import TravelAgent
    print("✓ TravelAgent 导入成功")
    
    print("\n所有模块导入成功！")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)
