"""测试景点门票工具 get_attraction_ticket_prices（真实调用高德地图API，不使用mock）"""
from __future__ import annotations

import io
import os
import sys

# 设置Windows控制台编码为UTF-8（避免日志中出现UnicodeEncodeError）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.tools import get_attraction_ticket_prices  # noqa: E402


def test_single_attraction(city: str, attraction_name: str = None, interests: str = None) -> None:
    """测试单个景点门票查询"""
    print(f"城市: {city}")
    if attraction_name:
        print(f"景点名称: {attraction_name}")
    if interests:
        print(f"兴趣偏好: {interests}")
    try:
        result = get_attraction_ticket_prices.invoke({
            "city": city,
            "attraction_name": attraction_name,
            "interests": interests
        })
        print("[成功] 返回结果：")
        print(result)
    except Exception as e:
        print(f"[失败] 调用异常: {e}")
        import traceback
        traceback.print_exc()
    print()


def main() -> None:
    """
    测试景点门票工具，测试用例写死在代码中，便于调试
    
    测试场景：
    - 指定景点名称查询
    - 根据兴趣偏好查询
    - 不同城市查询
    """
    # 测试用例（可修改）
    # (城市, 景点名称, 兴趣偏好)
    test_cases = [
        ("北京", "故宫", None),
        ("北京", None, "历史"),
        ("北京", None, "文化"),
        ("北京", None, "自然"),
        ("上海", "外滩", None),
        ("上海", None, "美食"),
        ("杭州", "西湖", None),
        ("杭州", None, "自然"),
        ("成都", None, "美食"),
        ("西安", "兵马俑", None),
    ]
    
    print("=" * 80)
    print("测试景点门票工具 get_attraction_ticket_prices")
    print("=" * 80)
    print(f"测试用例数量: {len(test_cases)}")
    print(f"AMAP_API_KEY: {'已配置' if bool(os.getenv('AMAP_API_KEY')) else '未配置（将无法获取天气）'}")
    print()
    
    # 测试每个用例
    for i, (city, attraction_name, interests) in enumerate(test_cases, 1):
        print(f"[测试 {i}/{len(test_cases)}]")
        test_single_attraction(city, attraction_name, interests)
        if i < len(test_cases):
            print("-" * 80)
            print()
    
    # 总结
    print("=" * 80)
    print("测试完成")
    print("=" * 80)
    print(f"共测试 {len(test_cases)} 个用例")
    print(f"测试城市: {', '.join(set(case[0] for case in test_cases))}")


if __name__ == "__main__":
    main()
