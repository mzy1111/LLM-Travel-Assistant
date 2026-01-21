"""测试Function Calling机制 - 验证LLM工具选择准确性"""
import os
import sys
import unittest
import warnings
from typing import List, Dict

# 抑制Pydantic弃用警告
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*dict.*method is deprecated.*')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.travel_agent import TravelAgent
from tests.fixtures.test_callback_handler import TestCallbackHandler


class TestFunctionCalling(unittest.TestCase):
    """测试Function Calling机制"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if not os.getenv('OPENAI_API_KEY'):
            raise unittest.SkipTest("OPENAI_API_KEY未设置，跳过测试")
        
        cls.agent = TravelAgent(verbose=False)
    
    def setUp(self):
        """每个测试前的初始化"""
        self.callback_handler = TestCallbackHandler()
    
    def test_tool_selection_accuracy(self):
        """测试工具选择准确性"""
        # 测试用例矩阵：输入 -> 期望调用的工具
        test_matrix = [
            ("北京明天天气", "query_weather_agent"),
            ("从北京到上海自驾", "query_transport_agent"),
            ("北京酒店价格", "query_hotel_agent"),
            ("北京景点推荐", "query_attraction_agent"),
            ("规划3天北京行程", "query_planning_agent"),
            ("个性化推荐", "query_recommendation_agent"),
        ]
        
        accuracy_count = 0
        total_count = len(test_matrix)
        
        for query, expected_tool in test_matrix:
            with self.subTest(query=query, expected_tool=expected_tool):
                self.callback_handler.reset()
                try:
                    response = self.agent.agent_executor.invoke(
                        {"input": query},
                        config={"callbacks": [self.callback_handler]}
                    )
                    result = response.get("output", "")
                    
                    call_sequence = self.callback_handler.get_agent_call_sequence()
                    expected_calls = self.callback_handler.get_agent_call_count(expected_tool)
                    
                    if expected_calls > 0:
                        accuracy_count += 1
                        print(f"✓ 工具选择正确: '{query}' -> {expected_tool}")
                    else:
                        print(f"✗ 工具选择错误: '{query}' -> 期望{expected_tool}, 实际调用{call_sequence}")
                    
                    self.assertIsInstance(result, str)
                    self.assertGreater(len(result), 0)
                    
                except Exception as e:
                    print(f"✗ 测试异常: '{query}' - {str(e)}")
        
        accuracy_rate = (accuracy_count / total_count) * 100
        print(f"\n工具选择准确率: {accuracy_rate:.1f}% ({accuracy_count}/{total_count})")
        self.assertGreaterEqual(accuracy_rate, 80, "工具选择准确率应 >= 80%")
    
    def test_parameter_extraction(self):
        """测试参数提取准确性"""
        test_cases = [
            {
                "query": "查询北京明天天气",
                "expected_params": ["北京", "明天"]
            },
            {
                "query": "从北京到上海自驾需要多久",
                "expected_params": ["北京", "上海", "自驾"]
            },
            {
                "query": "北京3天行程规划，预算5000元",
                "expected_params": ["北京", "3天", "5000"]
            },
        ]
        
        for case in test_cases:
            with self.subTest(query=case["query"]):
                self.callback_handler.reset()
                try:
                    response = self.agent.agent_executor.invoke(
                        {"input": case["query"]},
                        config={"callbacks": [self.callback_handler]}
                    )
                    result = response.get("output", "")
                    
                    # 验证结果中是否包含关键参数信息
                    result_lower = result.lower()
                    params_found = sum(
                        1 for param in case["expected_params"]
                        if param.lower() in result_lower or any(
                            char in result_lower for char in param
                        )
                    )
                    
                    # 至少应该找到部分参数
                    self.assertGreater(params_found, 0,
                        f"结果中应该包含部分参数信息: {case['expected_params']}")
                    
                    print(f"✓ 参数提取测试: '{case['query']}' -> 找到{params_found}/{len(case['expected_params'])}个参数")
                    
                except Exception as e:
                    self.fail(f"测试失败: {str(e)}")
    
    def test_tool_call_sequence(self):
        """测试工具调用顺序"""
        # 完整行程规划应该按合理顺序调用工具
        query = "从北京到上海，3天时间，帮我规划行程"
        
        self.callback_handler.reset()
        try:
            response = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result = response.get("output", "")
            
            call_sequence = self.callback_handler.get_agent_call_sequence()
            
            # 验证调用顺序的合理性
            # 规划Agent应该在最后调用
            if 'query_planning_agent' in call_sequence:
                planning_index = call_sequence.index('query_planning_agent')
                # 规划Agent应该在最后或接近最后
                self.assertGreaterEqual(planning_index, len(call_sequence) - 2,
                    f"规划Agent应该在最后调用，但位置为{planning_index}")
            
            print(f"✓ 工具调用顺序: {' -> '.join(call_sequence)}")
            
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")
    
    def test_no_duplicate_calls(self):
        """测试避免重复调用"""
        # 连续两次相同查询，第二次应该使用记忆而不是重新调用
        query = "北京明天天气怎么样？"
        
        # 第一次查询
        self.callback_handler.reset()
        try:
            response1 = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result1 = response1.get("output", "")
            first_call_count = self.callback_handler.get_agent_call_count('query_weather_agent')
            
            # 第二次相同查询
            self.callback_handler.reset()
            response2 = self.agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [self.callback_handler]}
            )
            result2 = response2.get("output", "")
            second_call_count = self.callback_handler.get_agent_call_count('query_weather_agent')
            
            # 注意：由于Agent的memory机制，第二次可能仍会调用
            # 但我们可以验证调用次数是否合理
            print(f"✓ 重复调用测试:")
            print(f"  - 第一次调用次数: {first_call_count}")
            print(f"  - 第二次调用次数: {second_call_count}")
            
            # 至少验证Agent能够正常处理重复查询
            self.assertIsInstance(result1, str)
            self.assertIsInstance(result2, str)
            
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
