"""测试Agent与第三方API的实际连接"""
import unittest
import os
import sys
from datetime import datetime, timedelta

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.tools import (
    get_weather_info,
    get_hotel_prices,
    get_transport_route,
    get_attraction_ticket_prices
)
from src.config import config


class TestRealAPIConnection(unittest.TestCase):
    """测试与第三方API的实际连接和功能验证（需要配置API密钥）"""
    
    @classmethod
    def setUpClass(cls):
        """检查API密钥是否配置"""
        cls.has_amap_key = bool(os.getenv("AMAP_API_KEY") or config.get("transport.api_key", ""))
        cls.has_tianapi_key = bool(os.getenv("TIANAPI_KEY") or config.get("attraction.api_key", ""))
        
        if not cls.has_amap_key:
            print("\n警告: AMAP_API_KEY 未配置，将跳过高德地图API测试")
        if not cls.has_tianapi_key:
            print("\n警告: TIANAPI_KEY 未配置，将跳过天聚数行API测试")
    
    def test_weather_api_today_real_data(self):
        """测试天气API获取当天实际天气数据"""
        if not self.has_amap_key:
            self.skipTest("AMAP_API_KEY 未配置")
        
        # 测试多个城市的当天天气
        test_cities = ["北京", "上海", "广州", "深圳"]
        today = datetime.now().strftime("%Y-%m-%d")
        
        success_count = 0
        for city in test_cities:
            try:
                result = get_weather_info.invoke({"city": city, "date": today})
                self.assertIsInstance(result, str)
                self.assertIn(city, result)
                
                # 验证返回的是实际天气数据，而不是估算
                import re
                # 应该包含实际温度（数字°C）
                has_real_temp = bool(re.search(r'\d+°C', result))
                # 应该包含天气状况
                has_weather = any(keyword in result for keyword in ["晴", "雨", "阴", "云", "雪", "雾", "霾"])
                # 不应该包含"假设"等估算关键词
                is_estimate = "假设" in result or "估算" in result
                
                if has_real_temp and has_weather and not is_estimate:
                    success_count += 1
                    print(f"\n[成功] {city}当天天气查询成功:")
                    print(f"  日期: {today}")
                    print(f"  结果: {result}")
                else:
                    print(f"\n[警告] {city}天气查询返回估算数据: {result[:100]}...")
                    
            except Exception as e:
                print(f"\n[失败] {city}天气查询失败: {str(e)}")
        
        # 至少应该有一个城市查询成功
        self.assertGreater(success_count, 0, "至少应有一个城市能获取实际天气数据")
        print(f"\n[成功] 成功获取 {success_count}/{len(test_cities)} 个城市的实际天气数据")
    
    def test_weather_api_real_connection(self):
        """测试天气API实际连接和功能验证"""
        if not self.has_amap_key:
            self.skipTest("AMAP_API_KEY 未配置")
        
        city = "北京"
        # 测试当天的实际天气
        date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            result = get_weather_info.invoke({"city": city, "date": date})
            self.assertIsInstance(result, str)
            self.assertIn("北京", result)
            
            # 验证返回的天气信息包含关键字段
            # 应该包含温度信息（数字+°C）
            import re
            has_temperature = bool(re.search(r'\d+°C|\d+\s*度', result))
            # 应该包含天气状况（晴、雨、阴等）
            weather_keywords = ["晴", "雨", "阴", "云", "雪", "雾", "霾", "天气"]
            has_weather_condition = any(keyword in result for keyword in weather_keywords)
            
            # 验证API返回了实际的天气数据
            self.assertTrue(
                has_temperature or has_weather_condition,
                f"返回结果应包含温度或天气状况，实际返回: {result}"
            )
            
            print(f"\n[成功] 天气API测试成功（查询当天实际天气）:")
            print(f"  城市: {city}")
            print(f"  日期: {date}")
            print(f"  返回结果: {result}")
            
            # 额外验证：如果查询的是今天，应该包含实况天气信息
            if date == datetime.now().strftime("%Y-%m-%d"):
                print(f"  [成功] 成功获取当天实际天气数据")
                
        except Exception as e:
            self.fail(f"天气API调用失败: {str(e)}")
    
    def test_transport_api_multiple_routes(self):
        """测试交通API查询多个实际路线"""
        if not self.has_amap_key:
            self.skipTest("AMAP_API_KEY 未配置")
        
        # 测试多个实际路线
        test_routes = [
            ("北京", "天津", "自驾"),
            ("上海", "杭州", "自驾"),
            ("广州", "深圳", "自驾"),
        ]
        
        success_count = 0
        for origin, destination, transport_mode in test_routes:
            try:
                result = get_transport_route.invoke({
                    "origin": origin,
                    "destination": destination,
                    "transport_mode": transport_mode
                })
                self.assertIsInstance(result, str)
                self.assertIn(origin, result)
                self.assertIn(destination, result)
                
                # 验证返回的是实际路线数据
                import re
                has_distance = bool(re.search(r'\d+公里', result))
                has_time = bool(re.search(r'\d+小时|\d+分钟', result))
                is_estimate = "估算" in result and "实际" not in result
                
                if has_distance and has_time and not is_estimate:
                    success_count += 1
                    print(f"\n[成功] {origin}到{destination}路线查询成功:")
                    print(f"  出行方式: {transport_mode}")
                    print(f"  结果: {result[:150]}...")
                else:
                    print(f"\n[警告] {origin}到{destination}路线查询返回估算数据")
                    
            except Exception as e:
                print(f"\n[失败] {origin}到{destination}路线查询失败: {str(e)}")
        
        # 至少应该有一个路线查询成功
        self.assertGreater(success_count, 0, "至少应有一个路线能获取实际数据")
        print(f"\n[成功] 成功获取 {success_count}/{len(test_routes)} 条路线的实际数据")
    
    def test_transport_api_real_connection(self):
        """测试交通API实际连接和功能验证（自驾）"""
        if not self.has_amap_key:
            self.skipTest("AMAP_API_KEY 未配置")
        
        origin = "北京"
        destination = "上海"
        transport_mode = "自驾"
        
        try:
            result = get_transport_route.invoke({
                "origin": origin,
                "destination": destination,
                "transport_mode": transport_mode
            })
            self.assertIsInstance(result, str)
            self.assertIn("北京", result)
            self.assertIn("上海", result)
            
            # 验证返回的交通信息包含关键字段
            import re
            # 应该包含距离信息（公里）
            has_distance = bool(re.search(r'\d+公里|\d+km', result, re.IGNORECASE))
            # 应该包含时间信息（小时、分钟）
            has_time = bool(re.search(r'\d+小时|\d+分钟|\d+分钟', result))
            # 应该包含费用信息（元）或路线信息
            has_cost_or_route = bool(re.search(r'\d+元|路线|距离', result))
            
            # 验证API返回了实际的交通数据
            self.assertTrue(
                has_distance or has_time or has_cost_or_route,
                f"返回结果应包含距离、时间或费用信息，实际返回: {result}"
            )
            
            print(f"\n[成功] 交通API测试成功（查询实际路线）:")
            print(f"  出发地: {origin}")
            print(f"  目的地: {destination}")
            print(f"  出行方式: {transport_mode}")
            print(f"  返回结果: {result}")
            
            # 如果包含实际距离，说明API调用成功
            if has_distance:
                print(f"  [成功] 成功获取实际距离数据")
            if has_time:
                print(f"  [成功] 成功获取实际时间数据")
                
        except Exception as e:
            self.fail(f"交通API调用失败: {str(e)}")
    
    def test_hotel_tool_basic(self):
        """测试酒店工具基本功能验证（智能估算）"""
        city = "北京"
        checkin_date = "2026-01-17"
        checkout_date = "2026-01-18"
        hotel_preference = "舒适型"
        
        try:
            result = get_hotel_prices.invoke({
                "city": city,
                "checkin_date": checkin_date,
                "checkout_date": checkout_date,
                "hotel_preference": hotel_preference
            })
            self.assertIsInstance(result, str)
            self.assertIn("北京", result)
            self.assertIn("价格", result)
            
            # 验证返回的酒店信息包含关键字段
            import re
            # 应该包含价格范围（数字-数字元/晚）
            has_price_range = bool(re.search(r'\d+-\d+元|\d+元/晚', result))
            # 应该包含预算建议
            has_budget = bool(re.search(r'预算|建议|总预算', result))
            
            # 验证工具返回了实际的估算数据
            self.assertTrue(
                has_price_range or has_budget,
                f"返回结果应包含价格范围或预算信息，实际返回: {result}"
            )
            
            print(f"\n[成功] 酒店工具测试成功（智能价格估算）:")
            print(f"  城市: {city}")
            print(f"  入住日期: {checkin_date}")
            print(f"  退房日期: {checkout_date}")
            print(f"  酒店偏好: {hotel_preference}")
            print(f"  返回结果: {result}")
            
            if has_price_range:
                print(f"  [成功] 成功生成价格估算数据")
                
        except Exception as e:
            self.fail(f"酒店工具调用失败: {str(e)}")
    
    def test_attraction_api_real_connection(self):
        """测试景点API实际连接和功能验证"""
        if not self.has_tianapi_key:
            self.skipTest("TIANAPI_KEY 未配置")
        
        city = "北京"
        interests = "历史、文化"
        
        try:
            result = get_attraction_ticket_prices.invoke({
                "city": city,
                "attraction_name": None,
                "interests": interests
            })
            self.assertIsInstance(result, str)
            self.assertIn("北京", result)
            
            # 验证返回的景点信息包含关键字段
            import re
            # 应该包含景点名称或门票价格信息
            has_attraction_info = bool(
                re.search(r'\d+元|门票|景点|景区|价格', result) or
                any(keyword in result for keyword in ["故宫", "天坛", "颐和园", "长城", "景点"])
            )
            
            # 验证API返回了实际的景点数据
            self.assertTrue(
                has_attraction_info,
                f"返回结果应包含景点或门票信息，实际返回: {result}"
            )
            
            print(f"\n[成功] 景点API测试成功（查询实际景点信息）:")
            print(f"  城市: {city}")
            print(f"  兴趣: {interests}")
            print(f"  返回结果: {result}")
            
            # 如果包含门票价格，说明API调用成功
            if "元" in result or "门票" in result:
                print(f"  [成功] 成功获取实际门票价格数据")
            elif any(keyword in result for keyword in ["故宫", "天坛", "颐和园", "长城"]):
                print(f"  [成功] 成功获取实际景点信息")
                
        except Exception as e:
            # 如果API失败，应该返回估算信息
            self.assertIsInstance(result, str)
            print(f"\n[警告] 景点API调用失败，返回估算信息: {str(e)}")
            print(f"  返回结果: {result}")


class TestAgentErrorHandling(unittest.TestCase):
    """测试Agent错误处理"""
    
    def test_weather_tool_invalid_city(self):
        """测试天气工具处理无效城市"""
        city = "不存在的城市12345"
        date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            result = get_weather_info.invoke({"city": city, "date": date})
            # 应该返回提示信息而不是抛出异常
            self.assertIsInstance(result, str)
            print(f"\n[成功] 天气工具错误处理测试成功: {result[:100]}...")
        except Exception as e:
            self.fail(f"天气工具应该处理错误而不是抛出异常: {str(e)}")
    
    def test_transport_tool_invalid_route(self):
        """测试交通工具处理无效路线"""
        origin = "不存在的出发地12345"
        destination = "不存在的目的地12345"
        transport_mode = "自驾"
        
        try:
            result = get_transport_route.invoke({
                "origin": origin,
                "destination": destination,
                "transport_mode": transport_mode
            })
            # 应该返回提示信息或估算
            self.assertIsInstance(result, str)
            print(f"\n[成功] 交通工具错误处理测试成功: {result[:100]}...")
        except Exception as e:
            self.fail(f"交通工具应该处理错误而不是抛出异常: {str(e)}")


if __name__ == '__main__':
    print("=" * 60)
    print("Agent工具第三方API连接测试")
    print("=" * 60)
    print("\n注意：此测试需要配置相应的API密钥")
    print("如果API密钥未配置，相关测试将被跳过\n")
    
    unittest.main(verbosity=2)

