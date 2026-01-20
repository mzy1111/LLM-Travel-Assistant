"""测试酒店价格工具 get_hotel_prices（真实调用，不使用mock）"""
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

from src.agent.tools import get_hotel_prices  # noqa: E402


def _date_str(days_offset: int) -> str:
    """获取距离今天指定天数的日期字符串"""
    return (datetime.now() + timedelta(days=days_offset)).strftime("%Y-%m-%d")


def test_single_hotel(city: str, hotel_preference: str, checkin_date: str, checkout_date: str) -> None:
    """测试单个酒店价格查询"""
    print(f"城市: {city}, 酒店类型: {hotel_preference}")
    print(f"入住日期: {checkin_date}, 退房日期: {checkout_date}")
    try:
        result = get_hotel_prices.invoke({
            "city": city,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "hotel_preference": hotel_preference
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
    测试酒店价格工具，测试用例写死在代码中，便于调试
    
    测试场景：
    - 不同城市（北京、上海、杭州）
    - 不同酒店类型（经济型、商务型、豪华型、民宿、青旅）
    - 不同日期（明天、一周后）
    """
    # 测试用例（可修改）
    test_cases = [
        # (城市, 酒店类型, 入住日期偏移, 退房日期偏移)
        ("北京", "商务型", 1, 4),  # 明天入住，4天后退房
        ("北京", "经济型", 1, 4),
        ("北京", "豪华型", 1, 4),
        ("上海", "商务型", 1, 3),
        ("杭州", "民宿", 1, 5),
        ("成都", "青旅", 1, 4),
    ]
    
    print("=" * 80)
    print("测试酒店价格工具 get_hotel_prices")
    print("=" * 80)
    print(f"测试用例数量: {len(test_cases)}")
    print()
    
    # 测试每个用例
    for i, (city, hotel_type, checkin_offset, checkout_offset) in enumerate(test_cases, 1):
        checkin_date = _date_str(checkin_offset)
        checkout_date = _date_str(checkout_offset)
        print(f"[测试 {i}/{len(test_cases)}]")
        test_single_hotel(city, hotel_type, checkin_date, checkout_date)
        if i < len(test_cases):
            print("-" * 80)
            print()
    
    # 总结
    print("=" * 80)
    print("测试完成")
    print("=" * 80)
    print(f"共测试 {len(test_cases)} 个用例")
    print(f"测试城市: {', '.join(set(case[0] for case in test_cases))}")
    print(f"测试酒店类型: {', '.join(set(case[1] for case in test_cases))}")


if __name__ == "__main__":
    main()
