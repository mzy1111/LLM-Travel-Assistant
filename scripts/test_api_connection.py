"""测试API连接脚本"""
import sys
import io
from pathlib import Path

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
import requests
import json

def test_api_connection():
    """测试API连接"""
    print("=" * 60)
    print("API连接测试")
    print("=" * 60)
    
    # 检查配置
    print("\n1. 检查配置...")
    print(f"   API密钥: {config.openai_api_key[:10]}..." if config.openai_api_key else "   [X] API密钥未设置")
    print(f"   API地址: {config.openai_api_base}")
    print(f"   模型名称: {config.llm_model}")
    
    if not config.openai_api_key:
        print("\n[X] 错误: API密钥未设置")
        print("   请在 env 文件中设置 OPENAI_API_KEY")
        return False
    
    # 测试API连接
    print("\n2. 测试API连接...")
    try:
        # 测试模型列表接口
        headers = {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # 尝试获取模型列表
        models_url = f"{config.openai_api_base}/models"
        print(f"   请求URL: {models_url}")
        
        response = requests.get(models_url, headers=headers, timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   [OK] API连接成功！")
            models = response.json()
            if 'data' in models:
                print(f"   可用模型数量: {len(models['data'])}")
                # 显示前几个模型
                print("   部分可用模型:")
                for model in models['data'][:5]:
                    print(f"     - {model.get('id', 'N/A')}")
            return True
        else:
            print(f"   [X] API请求失败")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"   [X] 连接错误: 无法连接到API服务器")
        print(f"   错误详情: {str(e)}")
        print("\n   可能的原因:")
        print("   1. 网络连接问题")
        print("   2. API服务地址不正确")
        print("   3. 防火墙或代理设置阻止了连接")
        return False
    except requests.exceptions.Timeout as e:
        print(f"   [X] 请求超时: API服务器响应时间过长")
        print(f"   错误详情: {str(e)}")
        return False
    except Exception as e:
        print(f"   [X] 未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试聊天接口
    print("\n3. 测试聊天接口...")
    try:
        chat_url = f"{config.openai_api_base}/chat/completions"
        print(f"   请求URL: {chat_url}")
        
        payload = {
            "model": config.llm_model,
            "messages": [
                {"role": "user", "content": "你好"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(
            chat_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   [OK] 聊天接口测试成功！")
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"   AI回复: {content}")
            return True
        else:
            print(f"   [X] 聊天接口测试失败")
            print(f"   错误信息: {response.text}")
            
            # 尝试解析错误
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_info = error_data['error']
                    print(f"\n   错误类型: {error_info.get('type', 'N/A')}")
                    print(f"   错误消息: {error_info.get('message', 'N/A')}")
                    if 'code' in error_info:
                        print(f"   错误代码: {error_info.get('code', 'N/A')}")
            except:
                pass
            
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"   [X] 连接错误: 无法连接到API服务器")
        print(f"   错误详情: {str(e)}")
        return False
    except Exception as e:
        print(f"   [X] 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_connection()
    print("\n" + "=" * 60)
    if success:
        print("[OK] 所有测试通过！API连接正常。")
    else:
        print("[X] 测试失败。请检查上述错误信息。")
    print("=" * 60)
    sys.exit(0 if success else 1)

