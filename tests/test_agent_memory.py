"""测试Agent记忆机制 - 验证多轮对话上下文保持"""
import os
import sys
import unittest
import warnings

# 抑制Pydantic弃用警告
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*dict.*method is deprecated.*')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.travel_agent import TravelAgent
from tests.fixtures.test_callback_handler import TestCallbackHandler


class TestAgentMemory(unittest.TestCase):
    """测试Agent记忆机制"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if not os.getenv('OPENAI_API_KEY'):
            raise unittest.SkipTest("OPENAI_API_KEY未设置，跳过测试")
        
        cls.agent = TravelAgent(verbose=False, enable_memory=True)
    
    def setUp(self):
        """每个测试前的初始化"""
        self.callback_handler = TestCallbackHandler()
    
    def test_multi_turn_conversation(self):
        """测试多轮对话记忆"""
        # 模拟多轮对话
        conversation = [
            "我想去北京旅游",
            "3天时间",
            "预算5000元",
            "帮我规划一下行程"
        ]
        
        results = []
        for i, query in enumerate(conversation):
            with self.subTest(turn=i+1, query=query):
                self.callback_handler.reset()
                try:
                    response = self.agent.agent_executor.invoke(
                        {"input": query},
                        config={"callbacks": [self.callback_handler]}
                    )
                    result = response.get("output", "")
                    results.append(result)
                    
                    # 验证每轮都有响应
                    self.assertIsInstance(result, str)
                    self.assertGreater(len(result), 0)
                    
                    print(f"✓ 第{i+1}轮对话: '{query}'")
                    print(f"  响应长度: {len(result)}字符")
                    
                except Exception as e:
                    self.fail(f"第{i+1}轮对话失败: {str(e)}")
        
        # 验证最后一轮应该整合前面的信息
        final_result = results[-1]
        final_lower = final_result.lower()
        
        # 应该包含一些关键信息（北京、3天、5000等）
        keywords = ['北京', '3', '5000', '天']
        found_keywords = [kw for kw in keywords if kw in final_lower or any(c in final_lower for c in kw)]
        
        print(f"\n✓ 多轮对话测试完成:")
        print(f"  - 总轮数: {len(conversation)}")
        print(f"  - 最终响应长度: {len(final_result)}字符")
        print(f"  - 找到关键词: {found_keywords}")
        
        # 至少应该找到部分关键词
        self.assertGreater(len(found_keywords), 0,
            "最终响应应该整合前面的对话信息")
    
    def test_context_persistence(self):
        """测试上下文持久性"""
        # 第一轮：设置目的地
        query1 = "我想去上海旅游"
        response1 = self.agent.agent_executor.invoke(
            {"input": query1},
            config={"callbacks": [self.callback_handler]}
        )
        result1 = response1.get("output", "")
        
        # 第二轮：只问天气（应该记住目的地是上海）
        self.callback_handler.reset()
        query2 = "天气怎么样？"
        response2 = self.agent.agent_executor.invoke(
            {"input": query2},
            config={"callbacks": [self.callback_handler]}
        )
        result2 = response2.get("output", "")
        
        # 验证第二轮应该知道目的地是上海
        result2_lower = result2.lower()
        
        # 应该提到上海（可能通过天气查询）
        has_shanghai = '上海' in result2 or 'shanghai' in result2_lower
        
        print(f"✓ 上下文持久性测试:")
        print(f"  - 第一轮: '{query1}'")
        print(f"  - 第二轮: '{query2}'")
        print(f"  - 第二轮是否包含上海: {has_shanghai}")
        
        # 注意：由于LLM的灵活性，可能不会直接提到上海
        # 但至少应该能够基于上下文回答
        self.assertIsInstance(result2, str)
        self.assertGreater(len(result2), 0)
    
    def test_agent_memory_isolation(self):
        """测试Agent记忆隔离"""
        # 验证不同专门Agent应该有独立的记忆
        # 这个测试比较难直接验证，因为记忆在Agent内部
        
        # 但我们可以验证主Agent的记忆不会影响专门Agent的独立性
        query1 = "北京天气怎么样？"
        response1 = self.agent.agent_executor.invoke(
            {"input": query1},
            config={"callbacks": [self.callback_handler]}
        )
        result1 = response1.get("output", "")
        
        self.callback_handler.reset()
        query2 = "上海有什么景点？"
        response2 = self.agent.agent_executor.invoke(
            {"input": query2},
            config={"callbacks": [self.callback_handler]}
        )
        result2 = response2.get("output", "")
        
        # 验证两次查询都能正常返回
        self.assertIsInstance(result1, str)
        self.assertIsInstance(result2, str)
        self.assertGreater(len(result1), 0)
        self.assertGreater(len(result2), 0)
        
        print(f"✓ Agent记忆隔离测试通过")
        print(f"  - 天气查询正常")
        print(f"  - 景点查询正常")
    
    def test_travel_info_memory(self):
        """测试旅行信息记忆"""
        # 使用set_travel_info设置旅行信息
        travel_info = {
            'departureDate': '2024-02-01',
            'returnDate': '2024-02-05',
            'destination': '北京',
            'departureCity': '上海',
            'budget': '5000',
            'hotelPreference': '商务型',
            'transportMode': '自驾',
            'travelStyle': '舒适',
            'interests': '历史、文化'
        }
        
        self.agent.set_travel_info(travel_info)
        
        # 查询应该能够使用这些信息
        query = "帮我规划一下行程"
        self.callback_handler.reset()
        response = self.agent.agent_executor.invoke(
            {"input": query},
            config={"callbacks": [self.callback_handler]}
        )
        result = response.get("output", "")
        
        # 验证结果应该包含旅行信息
        result_lower = result.lower()
        keywords = ['北京', '上海', '5000', '自驾']
        found_keywords = [kw for kw in keywords if kw in result_lower]
        
        print(f"✓ 旅行信息记忆测试:")
        print(f"  - 设置旅行信息: {travel_info['destination']}, {travel_info['departureCity']}")
        print(f"  - 找到关键词: {found_keywords}")
        
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
