"""测试专门Agent的功能"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.specialized_agents import (
    WeatherAgent,
    TransportAgent,
    HotelAgent,
    AttractionAgent,
    PlanningAgent,
    RecommendationAgent
)


class TestWeatherAgent(unittest.TestCase):
    """测试天气Agent"""
    
    @patch('src.agent.specialized_agents.config')
    @patch('src.agent.specialized_agents.ChatOpenAI')
    def test_weather_agent_creation(self, mock_llm, mock_config):
        """测试天气Agent创建"""
        # 模拟配置
        mock_config.get.return_value = True
        mock_config.openai_api_key = "test_key"
        mock_config.llm_model = "gpt-3.5-turbo"
        mock_config.openai_api_base = None
        
        # 模拟LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        try:
            agent = WeatherAgent(verbose=False)
            self.assertIsNotNone(agent.agent_executor)
            self.assertIsNotNone(agent.llm)
            print("\n✓ WeatherAgent 创建成功")
        except Exception as e:
            self.fail(f"WeatherAgent创建失败: {str(e)}")


class TestTransportAgent(unittest.TestCase):
    """测试交通Agent"""
    
    @patch('src.agent.specialized_agents.config')
    @patch('src.agent.specialized_agents.ChatOpenAI')
    def test_transport_agent_creation(self, mock_llm, mock_config):
        """测试交通Agent创建"""
        # 模拟配置
        mock_config.get.return_value = True
        mock_config.openai_api_key = "test_key"
        mock_config.llm_model = "gpt-3.5-turbo"
        mock_config.openai_api_base = None
        
        # 模拟LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        try:
            agent = TransportAgent(verbose=False)
            self.assertIsNotNone(agent.agent_executor)
            self.assertIsNotNone(agent.llm)
            print("\n✓ TransportAgent 创建成功")
        except Exception as e:
            self.fail(f"TransportAgent创建失败: {str(e)}")


class TestHotelAgent(unittest.TestCase):
    """测试酒店Agent"""
    
    @patch('src.agent.specialized_agents.config')
    @patch('src.agent.specialized_agents.ChatOpenAI')
    def test_hotel_agent_creation(self, mock_llm, mock_config):
        """测试酒店Agent创建"""
        # 模拟配置
        mock_config.get.return_value = True
        mock_config.openai_api_key = "test_key"
        mock_config.llm_model = "gpt-3.5-turbo"
        mock_config.openai_api_base = None
        
        # 模拟LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        try:
            agent = HotelAgent(verbose=False)
            self.assertIsNotNone(agent.agent_executor)
            self.assertIsNotNone(agent.llm)
            print("\n✓ HotelAgent 创建成功")
        except Exception as e:
            self.fail(f"HotelAgent创建失败: {str(e)}")


class TestAttractionAgent(unittest.TestCase):
    """测试景点Agent"""
    
    @patch('src.agent.specialized_agents.config')
    @patch('src.agent.specialized_agents.ChatOpenAI')
    def test_attraction_agent_creation(self, mock_llm, mock_config):
        """测试景点Agent创建"""
        # 模拟配置
        mock_config.get.return_value = True
        mock_config.openai_api_key = "test_key"
        mock_config.llm_model = "gpt-3.5-turbo"
        mock_config.openai_api_base = None
        
        # 模拟LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        try:
            agent = AttractionAgent(verbose=False)
            self.assertIsNotNone(agent.agent_executor)
            self.assertIsNotNone(agent.llm)
            print("\n✓ AttractionAgent 创建成功")
        except Exception as e:
            self.fail(f"AttractionAgent创建失败: {str(e)}")


class TestPlanningAgent(unittest.TestCase):
    """测试规划Agent"""
    
    @patch('src.agent.specialized_agents.config')
    @patch('src.agent.specialized_agents.ChatOpenAI')
    def test_planning_agent_creation(self, mock_llm, mock_config):
        """测试规划Agent创建"""
        # 模拟配置
        mock_config.get.return_value = True
        mock_config.openai_api_key = "test_key"
        mock_config.llm_model = "gpt-3.5-turbo"
        mock_config.openai_api_base = None
        
        # 模拟LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        try:
            agent = PlanningAgent(verbose=False)
            self.assertIsNotNone(agent.agent_executor)
            self.assertIsNotNone(agent.llm)
            print("\n✓ PlanningAgent 创建成功")
        except Exception as e:
            self.fail(f"PlanningAgent创建失败: {str(e)}")


class TestRecommendationAgent(unittest.TestCase):
    """测试推荐Agent"""
    
    @patch('src.agent.specialized_agents.config')
    @patch('src.agent.specialized_agents.ChatOpenAI')
    def test_recommendation_agent_creation(self, mock_llm, mock_config):
        """测试推荐Agent创建"""
        # 模拟配置
        mock_config.get.return_value = True
        mock_config.openai_api_key = "test_key"
        mock_config.llm_model = "gpt-3.5-turbo"
        mock_config.openai_api_base = None
        
        # 模拟LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        try:
            agent = RecommendationAgent(verbose=False)
            self.assertIsNotNone(agent.agent_executor)
            self.assertIsNotNone(agent.llm)
            print("\n✓ RecommendationAgent 创建成功")
        except Exception as e:
            self.fail(f"RecommendationAgent创建失败: {str(e)}")


if __name__ == '__main__':
    print("=" * 60)
    print("专门Agent功能测试")
    print("=" * 60)
    print("\n注意：此测试使用mock，不需要真实的API密钥\n")
    
    unittest.main(verbosity=2)

