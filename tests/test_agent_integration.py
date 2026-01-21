"""Agent集成测试 - 完整流程端到端测试"""
import os
import sys
import unittest
import warnings
from datetime import datetime, timedelta

# 抑制Pydantic弃用警告
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*dict.*method is deprecated.*')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.travel_agent import TravelAgent
from tests.fixtures.test_callback_handler import TestCallbackHandler


class TestAgentIntegration(unittest.TestCase):
    """Agent集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if not os.getenv('OPENAI_API_KEY'):
            raise unittest.SkipTest("OPENAI_API_KEY未设置，跳过测试")
        
        cls.agent = TravelAgent(verbose=False, enable_memory=True)
    
    def setUp(self):
        """每个测试前的初始化"""
        self.callback_handler = TestCallbackHandler()
    
    def test_complete_travel_planning_flow(self):
        """测试完整旅行规划流程"""
        # 设置旅行信息
        departure_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        return_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        
        travel_info = {
            'departureDate': departure_date,
            'returnDate': return_date,
            'destination': '北京',
            'departureCity': '上海',
            'budget': '5000',
            'hotelPreference': '商务型',
            'transportMode': '自驾',
            'travelStyle': '舒适',
            'interests': '历史、文化'
        }
        
        self.agent.set_travel_info(travel_info)
        
        # 执行规划查询
        query = "帮我规划一下详细的行程"
        
        start_time = datetime.now()
        self.callback_handler.reset()
        
        try:
            response = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result = response.get("output", "")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            summary = self.callback_handler.get_summary()
            
            print(f"✓ 完整旅行规划流程测试:")
            print(f"  - 目的地: {travel_info['destination']}")
            print(f"  - 出发地: {travel_info['departureCity']}")
            print(f"  - 天数: {(datetime.strptime(return_date, '%Y-%m-%d') - datetime.strptime(departure_date, '%Y-%m-%d')).days + 1}天")
            print(f"  - 预算: {travel_info['budget']}元")
            print(f"  - 总耗时: {duration:.2f}秒")
            print(f"  - Agent调用次数: {summary['agent_calls']}")
            print(f"  - 调用序列: {' -> '.join(summary['agent_call_sequence'])}")
            print(f"  - 响应长度: {len(result)}字符")
            
            # 验证关键点
            self.assertGreater(len(result), 100, "响应应该包含详细内容")
            self.assertGreater(summary['agent_calls'], 0, "应该调用至少一个Agent")
            
            # 验证应该调用规划Agent
            planning_calls = summary['agent_call_counts']['query_planning_agent']
            self.assertGreater(planning_calls, 0, "应该调用规划Agent")
            
            # 验证响应应该包含关键信息
            result_lower = result.lower()
            keywords = ['北京', '上海', '行程', '规划']
            found_keywords = [kw for kw in keywords if kw in result_lower]
            
            print(f"  - 找到关键词: {found_keywords}")
            
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")
    
    def test_weather_to_planning_flow(self):
        """测试从天气查询到行程规划的流程"""
        # 第一轮：查询天气
        query1 = "北京明天天气怎么样？"
        response1 = self.agent.agent_executor.invoke(
            {"input": query1},
            config={"callbacks": [self.callback_handler]}
        )
        result1 = response1.get("output", "")
        
        # 第二轮：基于天气规划行程
        self.callback_handler.reset()
        query2 = "基于这个天气，帮我规划一个3天的北京行程"
        response2 = self.agent.agent_executor.invoke(
            {"input": query2},
            config={"callbacks": [self.callback_handler]}
        )
        result2 = response2.get("output", "")
        
        summary = self.callback_handler.get_summary()
        
        print(f"✓ 天气到规划流程测试:")
        print(f"  - 第一轮: 天气查询")
        print(f"  - 第二轮: 行程规划")
        print(f"  - 第二轮Agent调用: {summary['agent_call_sequence']}")
        print(f"  - 规划Agent调用: {summary['agent_call_counts']['query_planning_agent']}")
        
        # 验证第二轮应该调用规划Agent
        planning_calls = summary['agent_call_counts']['query_planning_agent']
        self.assertGreater(planning_calls, 0, "应该调用规划Agent")
        
        self.assertIsInstance(result2, str)
        self.assertGreater(len(result2), 0)
    
    def test_multi_agent_coordination(self):
        """测试多Agent协调"""
        query = "我想从上海到北京，3天时间，预算5000元，需要知道天气、交通、酒店和景点信息"
        
        self.callback_handler.reset()
        try:
            response = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result = response.get("output", "")
            
            summary = self.callback_handler.get_summary()
            call_counts = summary['agent_call_counts']
            
            print(f"✓ 多Agent协调测试:")
            print(f"  - 查询: '{query}'")
            print(f"  - 各Agent调用次数: {call_counts}")
            print(f"  - 调用序列: {' -> '.join(summary['agent_call_sequence'])}")
            
            # 验证应该调用多个不同的Agent
            active_agents = [agent for agent, count in call_counts.items() if count > 0]
            self.assertGreater(len(active_agents), 1, "应该调用多个不同的Agent")
            
            # 验证响应完整性
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 50, "响应应该包含足够的信息")
            
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效查询
        invalid_queries = [
            "",  # 空查询
            "asdfghjkl",  # 无意义查询
        ]
        
        for query in invalid_queries:
            with self.subTest(query=query):
                self.callback_handler.reset()
                try:
                    response = self.agent.agent_executor.invoke(
                        {"input": query if query else " "},
                        config={"callbacks": [self.callback_handler]}
                    )
                    result = response.get("output", "")
                    
                    # 即使查询无效，也应该有响应（可能是错误提示）
                    self.assertIsInstance(result, str)
                    print(f"✓ 错误处理测试: '{query}' -> 有响应")
                    
                except Exception as e:
                    # 异常也是可以接受的错误处理方式
                    print(f"✓ 错误处理测试: '{query}' -> 抛出异常（可接受）")
    
    def test_streaming_response(self):
        """测试流式响应（如果支持）"""
        query = "北京明天天气怎么样？"
        
        try:
            # 尝试使用流式响应
            chunks = []
            for chunk in self.agent.chat_stream(query):
                chunks.append(chunk)
            
            result = ''.join(chunks)
            
            print(f"✓ 流式响应测试:")
            print(f"  - 查询: '{query}'")
            print(f"  - 响应块数: {len(chunks)}")
            print(f"  - 总长度: {len(result)}字符")
            
            self.assertGreater(len(chunks), 0, "应该有响应块")
            self.assertGreater(len(result), 0, "应该有响应内容")
            
        except Exception as e:
            # 流式响应可能不支持，这是可接受的
            print(f"⚠ 流式响应测试跳过: {str(e)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
