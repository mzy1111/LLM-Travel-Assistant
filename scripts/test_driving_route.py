"""测试自驾路线函数"""
from typing import Any


import os
import sys
import io

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.tools import _get_driving_route
from src.config import config

def test_driving_route():
    """测试自驾路线函数"""
    print("=" * 80)
    print("测试自驾路线函数 (_get_driving_route)")
    print("=" * 80)
    
    # 获取API密钥
    api_key = os.getenv("AMAP_API_KEY") or config.get("transport.api_key", "")
    
    if not api_key:
        print("\n[警告] AMAP_API_KEY 未配置，将使用测试密钥（可能失败）")
        api_key = "test_key"
    
    # 测试用例
    test_cases = [
        {
            "name": "测试1: 北京到天津",
            "origin": "北京",
            "destination": "天津",
            "api_key": api_key
        },
        {
            "name": "测试2: 详细地址",
            "origin": "北京市天安门广场",
            "destination": "天津市和平区",
            "api_key": api_key
        },
        {
            "name": "测试3: 省市区完整地址",
            "origin": "河北省廊坊市大厂回族自治县",
            "destination": "天津市",
            "api_key": api_key
        },
        {
            "name": "测试4: 无效地址（测试错误处理）",
            "origin": "不存在的城市12345",
            "destination": "不存在的城市67890",
            "api_key": api_key
        }
    ]
    
    for i, test_case in enumerate[dict[str, Any]](test_cases, 1):
        print(f"\n{'-' * 80}")
        print(f"{test_case['name']}")
        print(f"{'-' * 80}")
        print(f"出发地: {test_case['origin']}")
        print(f"目的地: {test_case['destination']}")
        print(f"API密钥: {'已配置' if api_key != 'test_key' else '未配置（测试）'}")
        print()
        print("开始测试...")
        print()
        
        try:
            result = _get_driving_route(
                test_case['origin'],
                test_case['destination'],
                test_case['api_key']
            )
            
            print()
            print(f"[成功] 测试完成")
            print(f"\n返回结果:")
            print(result)
            print()
            
        except Exception as e:
            print(f"[失败] 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_driving_route()

