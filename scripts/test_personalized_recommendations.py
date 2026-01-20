"""测试个性化推荐工具 get_personalized_recommendations（真实调用，不使用mock）"""
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

from src.agent.tools import get_personalized_recommendations  # noqa: E402


def test_single_recommendation(destination: str, interests: str, travel_style: str = None) -> None:
    """测试单个个性化推荐"""
    print(f"目的地: {destination}")
    print(f"兴趣偏好: {interests}")
    if travel_style:
        print(f"旅行风格: {travel_style}")
    try:
        result = get_personalized_recommendations.invoke({
            "destination": destination,
            "interests": interests,
            "travel_style": travel_style
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
    测试个性化推荐工具，测试用例写死在代码中，便于调试
    
    测试场景：
    - 不同兴趣偏好
    - 不同旅行风格
    - 不同城市
    """
    # 测试用例（可修改）
    # (目的地, 兴趣偏好, 旅行风格)
    test_cases = [
        ("北京", "历史、文化", "深度游"),
        ("北京", "自然、风景", "休闲游"),
        ("上海", "美食、购物", "休闲游"),
        ("上海", "博物馆、艺术", "文化游"),
        ("杭州", "自然、美食", "休闲游"),
        ("成都", "美食、文化", "美食游"),
        ("西安", "历史、文化", "深度游"),
        ("成都", "自然、风景", None),  # 无旅行风格
    ]
    
    print("=" * 80)
    print("测试个性化推荐工具 get_personalized_recommendations")
    print("=" * 80)
    print(f"测试用例数量: {len(test_cases)}")
    print()
    
    # 测试每个用例
    for i, (destination, interests, travel_style) in enumerate(test_cases, 1):
        print(f"[测试 {i}/{len(test_cases)}]")
        test_single_recommendation(destination, interests, travel_style)
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
