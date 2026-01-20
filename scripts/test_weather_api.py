"""测试天气工具 get_weather_info（真实调用高德天气API，不使用mock）"""
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

from src.agent.tools import get_weather_info  # noqa: E402


def _date_str(days_offset: int) -> str:
    """获取距离今天指定天数的日期字符串"""
    return (datetime.now() + timedelta(days=days_offset)).strftime("%Y-%m-%d")


def test_single_date(city: str, date: str, days_offset: int) -> None:
    """测试单个日期的天气"""
    print(f"日期: {date} (距离今天{days_offset}天)")
    try:
        result = get_weather_info.invoke({"city": city, "date": date})
        print("[成功] 返回结果：")
        print(result)
    except Exception as e:
        print(f"[失败] 调用异常: {e}")
        import traceback
        traceback.print_exc()
    print()


def main() -> None:
    """
    测试天气工具，测试用例写死在代码中，便于调试
    
    测试场景：
    - 今天（0天，实况天气）
    - 明天（1天，预报天气）
    - 3天后（预报天气）
    - 4天后（预报天气，边界值）
    - 5天后（超过4天预报范围）
    - 10天后（超过4天预报范围）
    """
    # 测试城市（可修改）
    city = "北京"
    
    # 测试天数列表（可修改）
    # 负数表示过去，0表示今天，正数表示未来
    test_days = [0, 1, 3, 4, 5, 10]
    
    # 生成测试日期列表
    dates_to_test = [_date_str(days) for days in test_days]
    
    print("=" * 80)
    print("测试天气工具 get_weather_info")
    print("=" * 80)
    print(f"城市: {city}")
    print(f"测试天数: {test_days}")
    print(f"测试日期数量: {len(dates_to_test)}")
    print(f"AMAP_API_KEY: {'已配置' if bool(os.getenv('AMAP_API_KEY')) else '未配置（将无法获取天气）'}")
    print()
    
    # 测试每个日期
    for i, (days, date) in enumerate(zip(test_days, dates_to_test), 1):
        print(f"[测试 {i}/{len(dates_to_test)}] 距离今天{days}天")
        test_single_date(city, date, days)
        if i < len(dates_to_test):
            print("-" * 80)
            print()
    
    # 总结
    print("=" * 80)
    print("测试完成")
    print("=" * 80)
    print(f"共测试 {len(dates_to_test)} 个日期")
    print(f"测试城市: {city}")
    print(f"测试天数范围: {min(test_days)} 到 {max(test_days)} 天")


if __name__ == "__main__":
    main()


