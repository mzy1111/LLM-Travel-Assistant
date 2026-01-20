"""测试景点问答工具 answer_attraction_question（真实调用，不使用mock）"""
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

from src.agent.tools import answer_attraction_question  # noqa: E402


def test_single_question(question: str, attraction: str) -> None:
    """测试单个景点问答"""
    print(f"问题: {question}")
    print(f"景点: {attraction}")
    try:
        result = answer_attraction_question.invoke({
            "question": question,
            "attraction": attraction
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
    测试景点问答工具，测试用例写死在代码中，便于调试
    
    测试场景：
    - 不同问题类型（开放时间、门票价格、最佳游览时间等）
    - 不同景点
    """
    # 测试用例（可修改）
    # (问题, 景点)
    test_cases = [
        ("开放时间是什么", "故宫"),
        ("门票价格是多少", "故宫"),
        ("最佳游览时间是什么时候", "故宫"),
        ("有什么特色", "天坛"),
        ("需要多长时间游览", "颐和园"),
        ("开放时间和门票价格", "天安门"),
        ("有什么推荐", "长城"),
    ]
    
    print("=" * 80)
    print("测试景点问答工具 answer_attraction_question")
    print("=" * 80)
    print(f"测试用例数量: {len(test_cases)}")
    print()
    
    # 测试每个用例
    for i, (question, attraction) in enumerate(test_cases, 1):
        print(f"[测试 {i}/{len(test_cases)}]")
        test_single_question(question, attraction)
        if i < len(test_cases):
            print("-" * 80)
            print()
    
    # 总结
    print("=" * 80)
    print("测试完成")
    print("=" * 80)
    print(f"共测试 {len(test_cases)} 个用例")
    print(f"测试景点: {', '.join(set(case[1] for case in test_cases))}")


if __name__ == "__main__":
    main()
