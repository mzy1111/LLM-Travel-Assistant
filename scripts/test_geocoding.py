"""测试地理编码API，查看详细响应"""
import os
import sys
import io
import json
import requests

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import config

def test_geocoding(address: str):
    """测试地理编码API，显示详细响应"""
    api_key = os.getenv("AMAP_API_KEY") or config.get("transport.api_key", "")
    
    if not api_key:
        print(f"[错误] AMAP_API_KEY 未配置")
        return
    
    geo_url = "https://restapi.amap.com/v3/geocode/geo"
    geo_params = {
        "address": address,
        "key": api_key,
        "output": "json"
    }
    
    print(f"\n{'=' * 80}")
    print(f"测试地址: {address}")
    print(f"{'=' * 80}")
    
    try:
        response = requests.get(geo_url, params=geo_params, timeout=5)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nAPI响应JSON:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            print(f"\n解析结果:")
            print(f"  status: {data.get('status')}")
            print(f"  info: {data.get('info')}")
            print(f"  count: {data.get('count')}")
            
            if data.get("geocodes"):
                print(f"  geocodes数量: {len(data.get('geocodes', []))}")
                for i, geocode in enumerate(data.get('geocodes', [])[:3], 1):
                    print(f"\n  结果 {i}:")
                    print(f"    formatted_address: {geocode.get('formatted_address')}")
                    print(f"    location: {geocode.get('location')}")
                    print(f"    adcode: {geocode.get('adcode')}")
                    print(f"    level: {geocode.get('level')}")
            else:
                print(f"  geocodes: 无")
            
            # 判断逻辑
            print(f"\n判断逻辑:")
            status_ok = data.get("status") == "1"
            has_geocodes = bool(data.get("geocodes"))
            print(f"  status == '1': {status_ok}")
            print(f"  has geocodes: {has_geocodes}")
            print(f"  最终判断: {'成功' if (status_ok and has_geocodes) else '失败'}")
        else:
            print(f"HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 测试相同的地址
    test_addresses = [
        "天津",
        "天津市",
        "天津市和平区",
        "河北省廊坊市大厂回族自治县",
        "大厂回族自治县"
    ]
    
    for address in test_addresses:
        test_geocoding(address)
        print()

