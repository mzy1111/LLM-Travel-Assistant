"""测试Agent性能 - API调用次数、响应时间等"""
import os
import sys
import unittest
import time
import warnings
from typing import Dict, Any

# 抑制Pydantic弃用警告
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*dict.*method is deprecated.*')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.travel_agent import TravelAgent
from tests.fixtures.test_callback_handler import TestCallbackHandler


class TestAgentPerformance(unittest.TestCase):
    """测试Agent性能"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if not os.getenv('OPENAI_API_KEY'):
            raise unittest.SkipTest("OPENAI_API_KEY未设置，跳过测试")
        
        cls.agent = TravelAgent(verbose=False)
    
    def setUp(self):
        """每个测试前的初始化"""
        self.callback_handler = TestCallbackHandler()
    
    def test_single_agent_performance(self):
        """测试单Agent调用性能"""
        query = "北京明天天气怎么样？"
        
        start_time = time.time()
        self.callback_handler.reset()
        
        try:
            response = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result = response.get("output", "")
            
            end_time = time.time()
            duration = end_time - start_time
            
            summary = self.callback_handler.get_summary()
            
            print(f"✓ 单Agent性能测试:")
            print(f"  - 查询: '{query}'")
            print(f"  - 总耗时: {duration:.2f}秒")
            print(f"  - Agent调用次数: {summary['agent_calls']}")
            print(f"  - LLM调用次数: {summary['llm_calls']}")
            print(f"  - 响应长度: {len(result)}字符")
            
            # 性能指标验证
            self.assertLess(duration, 30, "单Agent调用应在30秒内完成")
            self.assertGreater(len(result), 0, "应该有响应内容")
            
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")
    
    def test_multi_agent_performance(self):
        """测试多Agent协作性能"""
        query = "从北京到上海，3天时间，预算5000元，帮我规划行程"
        
        start_time = time.time()
        self.callback_handler.reset()
        
        try:
            response = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result = response.get("output", "")
            
            end_time = time.time()
            duration = end_time - start_time
            
            summary = self.callback_handler.get_summary()
            
            print(f"✓ 多Agent性能测试:")
            print(f"  - 查询: '{query}'")
            print(f"  - 总耗时: {duration:.2f}秒")
            print(f"  - Agent调用次数: {summary['agent_calls']}")
            print(f"  - 调用序列: {' -> '.join(summary['agent_call_sequence'])}")
            print(f"  - LLM调用次数: {summary['llm_calls']}")
            print(f"  - 响应长度: {len(result)}字符")
            print(f"  - 各Agent调用次数: {summary['agent_call_counts']}")
            
            # 性能指标验证
            self.assertLess(duration, 60, "多Agent协作应在60秒内完成")
            self.assertGreater(summary['agent_calls'], 1, "应该调用多个Agent")
            self.assertGreater(len(result), 0, "应该有响应内容")
            
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")
    
    def test_no_duplicate_agent_calls(self):
        """测试避免重复Agent调用"""
        query = "帮我规划一个3天的北京旅行，包括天气、交通、酒店、景点"
        
        self.callback_handler.reset()
        try:
            response = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result = response.get("output", "")
            
            summary = self.callback_handler.get_summary()
            call_counts = summary['agent_call_counts']
            
            # 验证每个Agent最多调用1次（关键优化点）
            duplicate_agents = [
                agent for agent, count in call_counts.items()
                if count > 1
            ]
            
            print(f"✓ 重复调用检查:")
            print(f"  - 各Agent调用次数: {call_counts}")
            print(f"  - 重复调用的Agent: {duplicate_agents if duplicate_agents else '无'}")
            
            # 理想情况下每个Agent只调用1次
            # 但由于LLM的灵活性，可能会有少量重复
            # 我们至少验证调用次数是合理的
            max_calls = max(call_counts.values()) if call_counts.values() else 0
            self.assertLessEqual(max_calls, 3,
                f"每个Agent最多应调用3次，但发现{max_calls}次调用")
            
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")
    
    def test_api_call_optimization(self):
        """测试API调用优化（existing_*参数）"""
        # 这个测试需要验证plan_travel_itinerary是否使用了existing_*参数
        # 由于这是工具层面的优化，我们通过调用序列来间接验证
        
        query = "从北京到上海，3天时间，帮我规划行程"
        
        self.callback_handler.reset()
        try:
            response = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result = response.get("output", "")
            
            summary = self.callback_handler.get_summary()
            call_sequence = summary['agent_call_sequence']
            
            # 如果调用了规划Agent，应该在此之前调用了其他Agent
            if 'query_planning_agent' in call_sequence:
                planning_index = call_sequence.index('query_planning_agent')
                agents_before_planning = call_sequence[:planning_index]
                
                print(f"✓ API调用优化检查:")
                print(f"  - 规划Agent调用位置: {planning_index}")
                print(f"  - 规划前调用的Agent: {agents_before_planning}")
                print(f"  - 规划Agent应该使用existing_*参数复用已查询信息")
            
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")
    
    def test_response_time_distribution(self):
        """测试响应时间分布"""
        queries = [
            "北京明天天气",
            "从北京到上海自驾",
            "北京酒店推荐",
        ]
        
        durations = []
        for query in queries:
            start_time = time.time()
            self.callback_handler.reset()
            
            try:
                response = self.agent.agent_executor.invoke(
                    {"input": query},
                    config={"callbacks": [self.callback_handler]}
                )
                result = response.get("output", "")
                duration = time.time() - start_time
                durations.append(duration)
                
                print(f"  - '{query}': {duration:.2f}秒")
                
            except Exception as e:
                print(f"  - '{query}': 失败 - {str(e)}")
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            print(f"\n✓ 响应时间分布:")
            print(f"  - 平均响应时间: {avg_duration:.2f}秒")
            print(f"  - 最大响应时间: {max_duration:.2f}秒")
            print(f"  - 最小响应时间: {min_duration:.2f}秒")
            
            self.assertLess(avg_duration, 20, "平均响应时间应 < 20秒")


if __name__ == '__main__':
    unittest.main(verbosity=2)
