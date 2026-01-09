"""主程序入口"""
import sys
import os
from pathlib import Path

# 确保输出立即刷新（不缓冲）
try:
    # Python 3.7+
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except AttributeError:
    # Python 3.6 及以下版本
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, line_buffering=True)

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.travel_agent import TravelAgent
from src.config import config


def interactive_mode():
    """交互式对话模式"""
    print("=" * 60)
    print("欢迎使用智能旅行助手！")
    print("=" * 60)
    print("您可以问我：")
    print("- 规划行程：'帮我规划一个3天的北京行程'")
    print("- 景点问题：'故宫的开放时间是什么？'")
    print("- 个性化推荐：'我喜欢历史和文化，推荐一些北京的景点'")
    print("- 输入 'quit' 或 'exit' 退出")
    print("=" * 60)
    print()
    
    agent = TravelAgent()
    
    while True:
        try:
            user_input = input("\n您: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！祝您旅途愉快！")
                break
            
            print("\n助手: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n再见！祝您旅途愉快！")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")


def main():
    """主函数"""
    try:
        # 检查API密钥
        if not config.openai_api_key:
            print("错误：未设置 OPENAI_API_KEY 环境变量", flush=True)
            print("请在 .env 或 env 文件中设置您的 OpenAI API 密钥", flush=True)
            sys.exit(1)
        
        # 启动交互模式
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"\n程序运行出错: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

