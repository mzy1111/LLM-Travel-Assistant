"""测试Agent工具和第三方API调用"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.tools import (
    get_weather_info,
    get_hotel_prices,
    get_transport_route,
    get_attraction_ticket_prices,
    plan_travel_itinerary
)


class TestWeatherTool(unittest.TestCase):
    """测试天气查询工具"""
    
    def setUp(self):
        """设置测试环境"""
        self.city = "北京"
        self.date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    @patch('src.agent.tools.requests.get')
    def test_weather_api_success(self, mock_get):
        """测试天气API调用成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "1",
            "geocodes": [{
                "adcode": "110000",
                "formatted_address": "北京市"
            }]
        }
        mock_get.return_value = mock_response
        
        # 模拟天气API响应
        def side_effect(url, **kwargs):
            if "geocode" in url:
                return mock_response
            elif "weather" in url:
                weather_response = MagicMock()
                weather_response.status_code = 200
                weather_response.json.return_value = {
                    "status": "1",
                    "forecasts": [{
                        "casts": [{
                            "date": self.date,
                            "dayweather": "晴",
                            "daytemp": "25",
                            "nighttemp": "15"
                        }]
                    }]
                }
                return weather_response
            return mock_response
        
        mock_get.side_effect = side_effect
        
        # 设置API密钥
        os.environ["AMAP_API_KEY"] = "test_key"
        
        # 调用工具（LangChain工具需要使用字典参数）
        result = get_weather_info.invoke({"city": self.city, "date": self.date})
        
        # 验证结果
        self.assertIsInstance(result, str)
        self.assertIn("北京", result)
        self.assertIn("天气", result)
    
    def test_weather_api_no_key(self):
        """测试天气API密钥未配置"""
        # 清除API密钥
        if "AMAP_API_KEY" in os.environ:
            del os.environ["AMAP_API_KEY"]
        
        result = get_weather_info.invoke({"city": self.city, "date": self.date})
        
        # 应该返回提示信息
        self.assertIsInstance(result, str)
        self.assertIn("API密钥未配置", result)


class TestTransportTool(unittest.TestCase):
    """测试交通路线工具"""
    
    def setUp(self):
        """设置测试环境"""
        self.origin = "北京"
        self.destination = "上海"
        self.transport_mode = "自驾"
    
    @patch('src.agent.tools.requests.get')
    def test_transport_api_success(self, mock_get):
        """测试交通API调用成功（自驾）"""
        # 模拟地理编码响应
        geo_response = MagicMock()
        geo_response.status_code = 200
        geo_response.json.return_value = {
            "status": "1",
            "geocodes": [{
                "location": "116.397428,39.90923",
                "formatted_address": "北京市"
            }]
        }
        
        # 模拟路径规划响应
        route_response = MagicMock()
        route_response.status_code = 200
        route_response.json.return_value = {
            "status": "1",
            "route": {
                "paths": [{
                    "distance": "1200000",  # 1200公里
                    "duration": "43200",  # 12小时
                    "tolls": "500",
                    "toll_distance": "1000000"
                }]
            }
        }
        
        def side_effect(url, **kwargs):
            if "geocode" in url:
                return geo_response
            elif "direction" in url:
                return route_response
            return geo_response
        
        mock_get.side_effect = side_effect
        
        # 设置API密钥
        os.environ["AMAP_API_KEY"] = "test_key"
        
        # 调用工具（使用字典参数）
        result = get_transport_route.invoke({
            "origin": self.origin,
            "destination": self.destination,
            "transport_mode": self.transport_mode
        })
        
        # 验证结果
        self.assertIsInstance(result, str)
        self.assertIn("北京", result)
        self.assertIn("上海", result)
        self.assertIn("距离", result)
        self.assertIn("公里", result)
    
    def test_transport_estimate(self):
        """测试交通路线估算（无API密钥）"""
        # 清除API密钥
        if "AMAP_API_KEY" in os.environ:
            del os.environ["AMAP_API_KEY"]
        
        result = get_transport_route.invoke({
            "origin": self.origin,
            "destination": self.destination,
            "transport_mode": "飞机"
        })
        
        # 应该返回估算信息
        self.assertIsInstance(result, str)
        self.assertIn("北京", result)
        self.assertIn("上海", result)


class TestHotelTool(unittest.TestCase):
    """测试酒店价格工具"""
    
    def setUp(self):
        """设置测试环境"""
        self.city = "北京"
        self.checkin_date = "2026-01-17"
        self.checkout_date = "2026-01-18"
        self.hotel_preference = "舒适型"
    
    def test_hotel_estimation(self):
        """测试酒店价格估算"""
        result = get_hotel_prices.invoke({
            "city": self.city,
            "checkin_date": self.checkin_date,
            "checkout_date": self.checkout_date,
            "hotel_preference": self.hotel_preference
        })
        
        # 验证结果
        self.assertIsInstance(result, str)
        self.assertIn("北京", result)
        self.assertIn("价格", result)
        self.assertIn("元", result)


class TestAttractionTool(unittest.TestCase):
    """测试景点门票工具"""
    
    def setUp(self):
        """设置测试环境"""
        self.city = "北京"
        self.interests = "历史、文化"
    
    @patch('src.agent.tools.requests.get')
    def test_attraction_api_success(self, mock_get):
        """测试景点API调用成功"""
        # 模拟天聚数行API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 200,
            "newslist": [
                {
                    "name": "故宫",
                    "level": "AAAAA级景区",
                    "address": "北京市东城区",
                    "ticket": "60元",
                    "opentime": "08:30-17:00"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # 设置API密钥
        os.environ["TIANAPI_KEY"] = "test_key"
        
        # 调用工具（使用字典参数）
        result = get_attraction_ticket_prices.invoke({
            "city": self.city,
            "attraction_name": None,
            "interests": self.interests
        })
        
        # 验证结果
        self.assertIsInstance(result, str)
        self.assertIn("北京", result)
    
    def test_attraction_estimation(self):
        """测试景点门票估算（无API密钥）"""
        # 清除API密钥
        if "TIANAPI_KEY" in os.environ:
            del os.environ["TIANAPI_KEY"]
        if "AMAP_API_KEY" in os.environ:
            del os.environ["AMAP_API_KEY"]
        
        result = get_attraction_ticket_prices.invoke({
            "city": self.city,
            "attraction_name": None,
            "interests": self.interests
        })
        
        # 应该返回估算信息
        self.assertIsInstance(result, str)
        self.assertIn("北京", result)


class TestPlanningTool(unittest.TestCase):
    """测试行程规划工具"""
    
    def setUp(self):
        """设置测试环境"""
        self.days = 3
        self.destination = "北京"
        self.departure_city = "上海"
        self.transport_mode = "自驾"
        self.departure_date = "2026-01-17"
        self.return_date = "2026-01-19"
    
    def test_planning_tool_integration(self):
        """测试行程规划工具整合"""
        # 直接测试工具函数，不mock（因为工具函数内部会处理API调用失败的情况）
        # 这个测试主要验证工具函数能够正确整合信息
        
        # 调用工具（使用字典参数）
        result = plan_travel_itinerary.invoke({
            "days": self.days,
            "destination": self.destination,
            "departure_city": self.departure_city,
            "transport_mode": self.transport_mode,
            "departure_date": self.departure_date,
            "return_date": self.return_date
        })
        
        # 验证结果
        self.assertIsInstance(result, str)
        self.assertIn("北京", result)
        self.assertIn("3天", result or "3")
        
        # 验证结果包含规划相关的关键词
        result_lower = result.lower()
        self.assertTrue(
            "行程" in result or "规划" in result or "安排" in result or
            "交通" in result_lower or "天气" in result_lower or "酒店" in result_lower
        )


class TestSpecializedAgents(unittest.TestCase):
    """测试专门Agent"""
    
    @patch('src.agent.specialized_agents.config')
    def test_weather_agent_initialization(self, mock_config):
        """测试天气Agent初始化"""
        # 模拟配置
        mock_config.get.return_value = True
        mock_config.openai_api_key = "test_key"
        mock_config.llm_model = "gpt-3.5-turbo"
        mock_config.openai_api_base = None
        
        from src.agent.specialized_agents import WeatherAgent
        
        # 由于需要真实的LLM，这里只测试导入和基本结构
        # 实际测试需要mock LLM
        self.assertTrue(hasattr(WeatherAgent, 'query'))
        self.assertTrue(hasattr(WeatherAgent, '_create_agent'))


class TestToolIntegration(unittest.TestCase):
    """测试工具集成"""
    
    def test_all_tools_importable(self):
        """测试所有工具可以正常导入"""
        from src.agent.tools import (
            get_weather_info,
            get_hotel_prices,
            get_transport_route,
            get_attraction_ticket_prices,
            plan_travel_itinerary,
            answer_attraction_question,
            get_personalized_recommendations
        )
        
        # 验证所有工具都已导入
        self.assertTrue(callable(get_weather_info.invoke))
        self.assertTrue(callable(get_hotel_prices.invoke))
        self.assertTrue(callable(get_transport_route.invoke))
        self.assertTrue(callable(get_attraction_ticket_prices.invoke))
        self.assertTrue(callable(plan_travel_itinerary.invoke))
        self.assertTrue(callable(answer_attraction_question.invoke))
        self.assertTrue(callable(get_personalized_recommendations.invoke))


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)

