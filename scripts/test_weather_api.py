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


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _tomorrow_str() -> str:
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def main() -> None:
    # 支持命令行参数：
    # python scripts/test_weather_api.py 北京 2026-01-14
    # python scripts/test_weather_api.py 北京   （默认今天）
    city = sys.argv[1] if len(sys.argv) >= 2 else "北京"
    date = sys.argv[2] if len(sys.argv) >= 3 else _today_str()

    print("=" * 80)
    print("测试天气工具 get_weather_info")
    print("=" * 80)
    print(f"城市: {city}")
    print(f"日期: {date}")
    print(f"AMAP_API_KEY: {'已配置' if bool(os.getenv('AMAP_API_KEY')) else '未配置（将走兜底）'}")
    print()

    try:
        result = get_weather_info.invoke({"city": city, "date": date})
        print("[成功] 返回结果：")
        print(result)
    except Exception as e:
        print(f"[失败] 调用异常: {e}")

    # 再额外跑一组：明天（触发预报路径），便于验证逻辑
    print("\n" + "-" * 80)
    print("附加测试：明天（预报路径）")
    print("-" * 80)
    tomorrow = _tomorrow_str()
    print(f"城市: {city}")
    print(f"日期: {tomorrow}")
    print()
    try:
        result2 = get_weather_info.invoke({"city": city, "date": tomorrow})
        print("[成功] 返回结果：")
        print(result2)
    except Exception as e:
        print(f"[失败] 调用异常: {e}")


if __name__ == "__main__":
    main()


