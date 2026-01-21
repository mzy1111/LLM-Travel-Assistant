"""测试用CallbackHandler，用于追踪Agent调用和工具执行"""
import time
from typing import Dict, List, Any, Optional
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult


class TestCallbackHandler(BaseCallbackHandler):
    """测试用CallbackHandler，记录所有Agent调用和工具执行"""
    
    def __init__(self):
        super().__init__()
        self.tool_calls: List[Dict[str, Any]] = []  # 记录所有工具调用
        self.agent_actions: List[Dict[str, Any]] = []  # 记录所有Agent动作
        self.llm_calls: List[Dict[str, Any]] = []  # 记录LLM调用
        self.agent_finish: List[Dict[str, Any]] = []  # 记录Agent完成
        self.start_time = time.time()
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """工具开始执行"""
        tool_name = serialized.get('name', 'unknown')
        self.tool_calls.append({
            'tool': tool_name,
            'input': input_str,
            'timestamp': time.time(),
            'start_time': time.time() - self.start_time
        })
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """工具执行完成"""
        if self.tool_calls:
            self.tool_calls[-1]['output'] = output
            self.tool_calls[-1]['end_time'] = time.time() - self.start_time
            self.tool_calls[-1]['duration'] = self.tool_calls[-1]['end_time'] - self.tool_calls[-1]['start_time']
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """工具执行错误"""
        if self.tool_calls:
            self.tool_calls[-1]['error'] = str(error)
            self.tool_calls[-1]['end_time'] = time.time() - self.start_time
    
    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        """Agent执行动作（工具调用）"""
        self.agent_actions.append({
            'tool': action.tool,
            'input': action.tool_input,
            'log': action.log,
            'timestamp': time.time(),
            'time': time.time() - self.start_time
        })
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> None:
        """Agent完成"""
        self.agent_finish.append({
            'return_values': finish.return_values,
            'log': finish.log,
            'timestamp': time.time(),
            'time': time.time() - self.start_time
        })
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """LLM开始调用"""
        self.llm_calls.append({
            'prompts': prompts,
            'timestamp': time.time(),
            'start_time': time.time() - self.start_time
        })
    
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """LLM调用完成"""
        if self.llm_calls:
            self.llm_calls[-1]['response'] = response
            self.llm_calls[-1]['end_time'] = time.time() - self.start_time
            self.llm_calls[-1]['duration'] = (
                self.llm_calls[-1]['end_time'] - self.llm_calls[-1]['start_time']
            )
    
    def get_agent_call_count(self, agent_name: str) -> int:
        """获取指定Agent的调用次数"""
        return sum(1 for action in self.agent_actions if action['tool'] == agent_name)
    
    def get_agent_call_sequence(self) -> List[str]:
        """获取Agent调用序列"""
        return [action['tool'] for action in self.agent_actions]
    
    def get_tool_call_count(self, tool_name: str) -> int:
        """获取指定工具的调用次数"""
        return sum(1 for call in self.tool_calls if call['tool'] == tool_name)
    
    def get_total_duration(self) -> float:
        """获取总执行时间"""
        if not self.agent_finish:
            return time.time() - self.start_time
        return self.agent_finish[-1]['time']
    
    def get_llm_call_count(self) -> int:
        """获取LLM调用次数"""
        return len(self.llm_calls)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        return {
            'total_duration': self.get_total_duration(),
            'agent_calls': len(self.agent_actions),
            'agent_call_sequence': self.get_agent_call_sequence(),
            'tool_calls': len(self.tool_calls),
            'llm_calls': self.get_llm_call_count(),
            'agent_call_counts': {
                agent: self.get_agent_call_count(agent)
                for agent in [
                    'query_weather_agent',
                    'query_transport_agent',
                    'query_hotel_agent',
                    'query_attraction_agent',
                    'query_planning_agent',
                    'query_recommendation_agent'
                ]
            }
        }
    
    def reset(self):
        """重置所有记录"""
        self.tool_calls = []
        self.agent_actions = []
        self.llm_calls = []
        self.agent_finish = []
        self.start_time = time.time()
