"""测试Agent路由机制 - 验证主Agent正确路由到专门Agent"""
# 必须在最前面导入并设置警告过滤
import warnings
import os
import sys

# 在导入任何其他模块之前抑制所有警告
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*dict.*method is deprecated.*')
warnings.filterwarnings('ignore', message='.*model_dump.*')
warnings.filterwarnings('ignore', message='.*PydanticDeprecatedSince20.*')
warnings.filterwarnings('ignore', message='.*The `dict` method is deprecated.*')
warnings.filterwarnings('ignore', message='.*is deprecated.*')
warnings.filterwarnings('ignore', module='pydantic.*')

# 导入测试模块的__init__以应用全局警告过滤
try:
    import tests
except ImportError:
    pass

import unittest
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入模块（警告已被抑制）
from src.agent.travel_agent import TravelAgent
from tests.fixtures.test_callback_handler import TestCallbackHandler


class TestAgentRouting(unittest.TestCase):
    """测试Agent路由功能"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 检查必要的环境变量
        if not os.getenv('OPENAI_API_KEY'):
            raise unittest.SkipTest("OPENAI_API_KEY未设置，跳过测试")
        
        # 创建测试用的Agent实例
        cls.agent = TravelAgent(verbose=False)
    
    def setUp(self):
        """每个测试前的初始化"""
        self.callback_handler = TestCallbackHandler()
    
    def test_weather_routing(self):
        """测试天气查询路由"""
        test_cases = [
            "请查询北京明天的天气",
            "我想知道上海今天的天气",
            "请查询广州3天后的天气预报",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                self.callback_handler.reset()
                try:
                    response = self.agent.agent_executor.invoke(
                        {"input": query},
                        config={"callbacks": [self.callback_handler]}
                    )
                    result = response.get("output", "")
                    
                    # 验证应该调用天气Agent
                    call_sequence = self.callback_handler.get_agent_call_sequence()
                    weather_calls = self.callback_handler.get_agent_call_count('query_weather_agent')
                    
                    # 如果LLM没有调用Agent，输出调试信息
                    if weather_calls == 0:
                        print(f"⚠️  警告: 查询'{query}'未调用天气Agent")
                        print(f"   调用序列: {call_sequence}")
                        print(f"   LLM响应: {result[:200]}...")
                        # 检查响应是否包含天气相关信息（LLM可能直接回答了）
                        weather_keywords = ['天气', '温度', '降雨', '晴天', '雨天', '多云', 'weather']
                        has_weather_info = any(keyword in result for keyword in weather_keywords)
                        if has_weather_info:
                            print(f"   ⚠️  LLM直接回答了天气问题，未调用Agent（这是可接受的，但不符合预期）")
                        # 仍然断言失败，因为我们的目标是测试路由功能
                    
                    self.assertGreater(weather_calls, 0, 
                        f"查询'{query}'应该调用天气Agent，但调用序列为: {call_sequence}，响应: {result[:100]}")
                    self.assertIsInstance(result, str)
                    self.assertGreater(len(result), 0)
                    
                    print(f"✓ 路由测试通过: '{query}' -> 天气Agent (调用{weather_calls}次)")
                    print(f"   Agent回答: {result}")
                    
                except Exception as e:
                    self.fail(f"测试失败: {str(e)}")
    
    def test_transport_routing(self):
        """测试交通路线路由"""
        test_cases = [
            "从北京到上海自驾需要多久？",
            "查询从广州到深圳的交通路线",
            "北京到天津的距离是多少？",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                self.callback_handler.reset()
                try:
                    response = self.agent.agent_executor.invoke(
                        {"input": query},
                        config={"callbacks": [self.callback_handler]}
                    )
                    result = response.get("output", "")
                    
                    call_sequence = self.callback_handler.get_agent_call_sequence()
                    transport_calls = self.callback_handler.get_agent_call_count('query_transport_agent')
                    
                    self.assertGreater(transport_calls, 0,
                        f"查询'{query}'应该调用交通Agent，但调用序列为: {call_sequence}")
                    
                    print(f"✓ 路由测试通过: '{query}' -> 交通Agent (调用{transport_calls}次)")
                    print(f"   Agent回答: {result}")
                    
                except Exception as e:
                    self.fail(f"测试失败: {str(e)}")
    
    def test_hotel_routing(self):
        """测试酒店查询路由"""
        test_cases = [
            "北京有什么酒店推荐？",
            "查询上海的经济型酒店价格",
            "广州的酒店价格是多少？",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                self.callback_handler.reset()
                try:
                    response = self.agent.agent_executor.invoke(
                        {"input": query},
                        config={"callbacks": [self.callback_handler]}
                    )
                    result = response.get("output", "")
                    
                    call_sequence = self.callback_handler.get_agent_call_sequence()
                    hotel_calls = self.callback_handler.get_agent_call_count('query_hotel_agent')
                    
                    self.assertGreater(hotel_calls, 0,
                        f"查询'{query}'应该调用酒店Agent，但调用序列为: {call_sequence}")
                    
                    print(f"✓ 路由测试通过: '{query}' -> 酒店Agent (调用{hotel_calls}次)")
                    print(f"   Agent回答: {result}")
                    
                except Exception as e:
                    self.fail(f"测试失败: {str(e)}")
    
    def test_attraction_routing(self):
        """测试景点查询路由"""
        test_cases = [
            "北京有什么景点？",
            "推荐一些上海的旅游景点",
            "广州有哪些历史景点？",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                self.callback_handler.reset()
                try:
                    response = self.agent.agent_executor.invoke(
                        {"input": query},
                        config={"callbacks": [self.callback_handler]}
                    )
                    result = response.get("output", "")
                    
                    call_sequence = self.callback_handler.get_agent_call_sequence()
                    attraction_calls = self.callback_handler.get_agent_call_count('query_attraction_agent')
                    
                    self.assertGreater(attraction_calls, 0,
                        f"查询'{query}'应该调用景点Agent，但调用序列为: {call_sequence}")
                    
                    print(f"✓ 路由测试通过: '{query}' -> 景点Agent (调用{attraction_calls}次)")
                    print(f"   Agent回答: {result}")
                    
                except Exception as e:
                    self.fail(f"测试失败: {str(e)}")
    
    def test_planning_routing(self):
        """测试行程规划路由"""
        test_cases = [
            "帮我规划一个3天的北京旅行",
            "制定一个上海5天的行程计划",
            "我想去广州旅游，帮我规划一下",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                self.callback_handler.reset()
                try:
                    response = self.agent.agent_executor.invoke(
                        {"input": query},
                        config={"callbacks": [self.callback_handler]}
                    )
                    result = response.get("output", "")
                    
                    call_sequence = self.callback_handler.get_agent_call_sequence()
                    planning_calls = self.callback_handler.get_agent_call_count('query_planning_agent')
                    
                    # 行程规划可能会先调用其他Agent，但最终应该调用规划Agent
                    self.assertGreater(planning_calls, 0,
                        f"查询'{query}'应该调用规划Agent，但调用序列为: {call_sequence}")
                    
                    print(f"✓ 路由测试通过: '{query}' -> 规划Agent (调用{planning_calls}次)")
                    print(f"   Agent回答: {result}")
                    
                except Exception as e:
                    self.fail(f"测试失败: {str(e)}")
    
    def test_multi_agent_routing(self):
        """测试多Agent协作路由"""
        # 完整行程规划应该调用多个Agent
        query = "我想从北京到上海，3天时间，预算5000元，帮我规划一下"
        
        self.callback_handler.reset()
        try:
            response = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result = response.get("output", "")
            
            call_sequence = self.callback_handler.get_agent_call_sequence()
            summary = self.callback_handler.get_summary()
            
            # 应该调用多个Agent
            total_agent_calls = summary['agent_calls']
            self.assertGreater(total_agent_calls, 1,
                f"完整规划应该调用多个Agent，但只调用了{total_agent_calls}个")
            
            # 应该最终调用规划Agent
            planning_calls = summary['agent_call_counts']['query_planning_agent']
            self.assertGreater(planning_calls, 0,
                f"完整规划应该调用规划Agent，但调用序列为: {call_sequence}")
            
            print(f"✓ 多Agent协作测试通过:")
            print(f"  - 总Agent调用次数: {total_agent_calls}")
            print(f"  - 调用序列: {' -> '.join(call_sequence)}")
            print(f"  - 各Agent调用次数: {summary['agent_call_counts']}")
            print(f"  - Agent回答: {result}")
            
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
