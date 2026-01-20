"""测试行程规划工具 plan_travel_itinerary（真实调用，不使用mock）"""
from __future__ import annotations

import io
import os
import sys
from datetime import datetime, timedelta

# 设置Windows控制台编码为UTF-8（避免日志中出现UnicodeEncodeError）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.tools import plan_travel_itinerary  # noqa: E402


def _date_str(days_offset: int) -> str:
    """获取距离今天指定天数的日期字符串"""
    return (datetime.now() + timedelta(days=days_offset)).strftime("%Y-%m-%d")


def test_single_itinerary(
    days: int,
    destination: str = None,
    budget: float = None,
    departure_city: str = None,
    transport_mode: str = "自驾",
    departure_date: str = None,
    return_date: str = None,
    hotel_preference: str = "商务型",
    interests: str = "历史、文化"
) -> None:
    """测试单个行程规划"""
    print(f"天数: {days}")
    if destination:
        print(f"目的地: {destination}")
    if budget:
        print(f"预算: {budget}元")
    if departure_city:
        print(f"出发地: {departure_city}")
    print(f"出行方式: {transport_mode}")
    if departure_date:
        print(f"出发日期: {departure_date}")
    if return_date:
        print(f"返回日期: {return_date}")
    print(f"酒店偏好: {hotel_preference}")
    print(f"兴趣偏好: {interests}")
    try:
        result = plan_travel_itinerary.invoke({
            "days": days,
            "destination": destination,
            "budget": budget,
            "departure_city": departure_city,
            "transport_mode": transport_mode,
            "departure_date": departure_date,
            "return_date": return_date,
            "hotel_preference": hotel_preference,
            "interests": interests
        })
        print("[成功] 返回结果：")
        print(result[:1000] + "..." if len(result) > 1000 else result)
    except Exception as e:
        print(f"[失败] 调用异常: {e}")
        import traceback
        traceback.print_exc()
    print()


def main() -> None:
    """
    测试行程规划工具，测试用例写死在代码中，便于调试
    
    测试场景：
    - 完整信息（有出发地和目的地）
    - 无目的地（系统推荐）
    - 无出发地（仅目的地）
    """
    # 测试用例（可修改）
    # (天数, 目的地, 预算, 出发地, 出行方式, 出发日期偏移, 返回日期偏移, 酒店偏好, 兴趣偏好)
    test_cases = [
        (3, "北京", 5000, "上海", "自驾", 1, 4, "商务型", "历史、文化"),
        (5, "杭州", 3000, None, "自驾", 1, 6, "经济型", "自然、美食"),
        (3, "成都", 4000, None, "自驾", 1, 4, "商务型", "美食、文化"),
        (2, None, 5000, None, "自驾", 1, 3, "商务型", "历史、文化"),  # 无目的地
    ]
    
    print("=" * 80)
    print("测试行程规划工具 plan_travel_itinerary")
    print("=" * 80)
    print(f"测试用例数量: {len(test_cases)}")
    print(f"AMAP_API_KEY: {'已配置' if bool(os.getenv('AMAP_API_KEY')) else '未配置（将无法获取天气）'}")
    print()
    
    # 测试每个用例
    for i, (days, destination, budget, departure_city, transport_mode, 
            departure_offset, return_offset, hotel_preference, interests) in enumerate(test_cases, 1):
        departure_date = _date_str(departure_offset) if departure_offset else None
        return_date = _date_str(return_offset) if return_offset else None
        
        print(f"[测试 {i}/{len(test_cases)}]")
        test_single_itinerary(
            days=days,
            destination=destination,
            budget=budget,
            departure_city=departure_city,
            transport_mode=transport_mode,
            departure_date=departure_date,
            return_date=return_date,
            hotel_preference=hotel_preference,
            interests=interests
        )
        if i < len(test_cases):
            print("-" * 80)
            print()
    
    # 总结
    print("=" * 80)
    print("测试完成")
    print("=" * 80)
    print(f"共测试 {len(test_cases)} 个用例")


if __name__ == "__main__":
    main()
