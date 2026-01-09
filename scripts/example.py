"""使用示例"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.travel_agent import TravelAgent
from src.config import config


def example_usage():
    """示例用法"""
    print("=" * 60)
    print("智能旅行助手 - 使用示例")
    print("=" * 60)
    
    # 检查API密钥
    if not config.openai_api_key:
        print("错误：请先设置 OPENAI_API_KEY 环境变量")
        print("复制 env.example 为 .env 并填入您的API密钥")
        return
    
    # 创建Agent
    print("\n1. 创建智能旅行助手...")
    agent = TravelAgent(verbose=True)
    print("   Agent创建完成")
    
    # 示例对话
    print("\n2. 开始示例对话...")
    print("=" * 60)
    
    examples = [
        "北京有哪些著名景点？",
        "帮我规划一个3天的北京行程，预算5000元",
        "故宫的开放时间是什么？",
        "我喜欢历史和文化，推荐一些北京的景点"
    ]
    
    for i, query in enumerate(examples, 1):
        print(f"\n示例 {i}:")
        print(f"用户: {query}")
        print(f"助手: ", end="", flush=True)
        response = agent.chat(query)
        print(response)
        print("-" * 60)
    
    print("\n示例完成！")
    print("运行 'python src/main.py' 进入交互模式")


if __name__ == "__main__":
    example_usage()
