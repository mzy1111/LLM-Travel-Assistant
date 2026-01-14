"""专门的Agent类，每个Agent负责特定领域的服务"""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from src.agent.tools import (
    get_weather_info,
    get_hotel_prices,
    get_transport_route,
    get_attraction_ticket_prices,
    answer_attraction_question,
    get_personalized_recommendations,
    plan_travel_itinerary
)
from src.config import config


class BaseSpecializedAgent:
    """专门Agent的基类"""
    
    def __init__(self, verbose: Optional[bool] = None):
        self.verbose = verbose if verbose is not None else config.get("agent.verbose", True)
        self.llm = self._create_llm()
        self.agent_executor = None
    
    def _create_llm(self):
        """创建LLM实例"""
        import os
        
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY 未设置，请在 env 文件中配置API密钥")
        
        os.environ["OPENAI_API_KEY"] = config.openai_api_key
        
        llm_kwargs = {
            "model": config.llm_model,
            "temperature": config.get("llm.temperature", 0.7),
            "openai_api_key": config.openai_api_key,
            "timeout": 60,
            "max_retries": 2,
        }
        
        if config.openai_api_base and "openai.com" not in config.openai_api_base:
            os.environ["OPENAI_API_BASE"] = config.openai_api_base
            llm_kwargs["openai_api_base"] = config.openai_api_base
        
        max_tokens = config.get("llm.max_tokens", 2000)
        if max_tokens:
            llm_kwargs["max_tokens"] = max_tokens
        
        return ChatOpenAI(**llm_kwargs)
    
    def query(self, user_input: str) -> str:
        """执行查询"""
        if not self.agent_executor:
            raise ValueError("Agent执行器未初始化")
        
        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response.get("output", "抱歉，我无法处理您的请求。")
        except Exception as e:
            if self.verbose:
                print(f"Agent执行错误: {e}", flush=True)
            return f"处理请求时出错: {str(e)}"


class WeatherAgent(BaseSpecializedAgent):
    """天气查询专用Agent"""
    
    def __init__(self, verbose: Optional[bool] = None):
        super().__init__(verbose)
        self.agent_executor = self._create_agent()
    
    def _create_agent(self):
        """创建天气Agent"""
        system_prompt = """你是一个专业的天气查询助手，专门负责查询和提供天气信息。

你的职责：
1. 使用 get_weather_info 工具查询指定城市在指定日期的天气信息
2. 根据天气情况提供旅行建议（如雨天推荐室内活动，晴天推荐户外活动）
3. 提供详细的天气信息，包括温度、天气状况、风向、风力等

重要原则：
- 必须使用 get_weather_info 工具查询天气，不要猜测或估算
- 提供准确、详细的天气信息
- 根据天气情况给出实用的旅行建议

回答要专业、准确、详细。"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=[get_weather_info],
            prompt=prompt
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return AgentExecutor(
            agent=agent,
            tools=[get_weather_info],
            memory=memory,
            verbose=self.verbose,
            max_iterations=5,
            handle_parsing_errors=True
        )


class TransportAgent(BaseSpecializedAgent):
    """交通路线专用Agent"""
    
    def __init__(self, verbose: Optional[bool] = None):
        super().__init__(verbose)
        self.agent_executor = self._create_agent()
    
    def _create_agent(self):
        """创建交通Agent"""
        system_prompt = """你是一个专业的交通路线规划助手，专门负责查询和提供交通路线信息。

你的职责：
1. 使用 get_transport_route 工具查询从出发地到目的地的交通路线
2. 提供详细的路线信息，包括距离、时间、费用等
3. 对于自驾方式，使用高德地图API进行精确计算

重要原则：
- 必须使用 get_transport_route 工具查询路线，不要猜测或估算
- 对于自驾方式，确保使用API精确计算距离和时间
- 提供准确的距离、时间、过路费、油费等信息
- 根据距离和时间提供驾驶建议

回答要专业、准确、详细。"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=[get_transport_route],
            prompt=prompt
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return AgentExecutor(
            agent=agent,
            tools=[get_transport_route],
            memory=memory,
            verbose=self.verbose,
            max_iterations=5,
            handle_parsing_errors=True
        )


class HotelAgent(BaseSpecializedAgent):
    """酒店价格专用Agent"""
    
    def __init__(self, verbose: Optional[bool] = None):
        super().__init__(verbose)
        self.agent_executor = self._create_agent()
    
    def _create_agent(self):
        """创建酒店Agent"""
        system_prompt = """你是一个专业的酒店价格查询助手，专门负责查询和提供酒店价格信息。

你的职责：
1. 使用 get_hotel_prices 工具查询指定城市在指定日期的酒店价格
2. 根据酒店偏好提供价格估算和建议
3. 提供详细的酒店价格信息，包括价格范围、总预算等

重要原则：
- 必须使用 get_hotel_prices 工具查询价格，不要猜测或估算
- 根据城市、季节、酒店类型提供准确的价格估算
- 提供实用的预订建议

回答要专业、准确、详细。"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=[get_hotel_prices],
            prompt=prompt
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return AgentExecutor(
            agent=agent,
            tools=[get_hotel_prices],
            memory=memory,
            verbose=self.verbose,
            max_iterations=5,
            handle_parsing_errors=True
        )


class AttractionAgent(BaseSpecializedAgent):
    """景点查询专用Agent"""
    
    def __init__(self, verbose: Optional[bool] = None):
        super().__init__(verbose)
        self.agent_executor = self._create_agent()
    
    def _create_agent(self):
        """创建景点Agent"""
        system_prompt = """你是一个专业的景点查询助手，专门负责查询和提供景点相关信息。

你的职责：
1. 使用 get_attraction_ticket_prices 工具查询景点门票价格
2. 使用 answer_attraction_question 工具回答景点相关问题
3. 提供详细的景点信息，包括门票价格、开放时间、地址等

重要原则：
- 必须使用相应的工具查询信息，不要猜测或估算
- 提供准确、详细的景点信息
- 根据用户兴趣推荐相关景点

回答要专业、准确、详细。"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=[get_attraction_ticket_prices, answer_attraction_question],
            prompt=prompt
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return AgentExecutor(
            agent=agent,
            tools=[get_attraction_ticket_prices, answer_attraction_question],
            memory=memory,
            verbose=self.verbose,
            max_iterations=5,
            handle_parsing_errors=True
        )


class PlanningAgent(BaseSpecializedAgent):
    """行程规划专用Agent"""
    
    def __init__(self, verbose: Optional[bool] = None):
        super().__init__(verbose)
        self.agent_executor = self._create_agent()
    
    def _create_agent(self):
        """创建规划Agent"""
        system_prompt = """你是一个专业的旅行行程规划助手，专门负责规划详细的旅行行程。

你的职责：
1. 使用 plan_travel_itinerary 工具规划详细的旅行行程
2. 整合天气、酒店、交通、景点等信息
3. 提供详细的每日行程安排，包括景点、餐饮、住宿、交通和预算分配

重要原则：
- 必须使用 plan_travel_itinerary 工具规划行程
- 该工具会自动查询和整合所有相关信息
- 提供详细、实用的行程安排
- 根据用户偏好和预算进行合理规划

回答要专业、详细、实用。"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=[plan_travel_itinerary],
            prompt=prompt
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return AgentExecutor(
            agent=agent,
            tools=[plan_travel_itinerary],
            memory=memory,
            verbose=self.verbose,
            max_iterations=5,
            handle_parsing_errors=True
        )


class RecommendationAgent(BaseSpecializedAgent):
    """个性化推荐专用Agent"""
    
    def __init__(self, verbose: Optional[bool] = None):
        super().__init__(verbose)
        self.agent_executor = self._create_agent()
    
    def _create_agent(self):
        """创建推荐Agent"""
        system_prompt = """你是一个专业的旅行推荐助手，专门负责提供个性化旅行推荐。

你的职责：
1. 使用 get_personalized_recommendations 工具提供个性化推荐
2. 根据用户兴趣、偏好、预算等提供推荐
3. 提供详细、实用的推荐列表

重要原则：
- 必须使用 get_personalized_recommendations 工具提供推荐
- 根据用户兴趣和偏好提供个性化推荐
- 提供详细、实用的推荐信息

回答要专业、个性化、详细。"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=[get_personalized_recommendations],
            prompt=prompt
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return AgentExecutor(
            agent=agent,
            tools=[get_personalized_recommendations],
            memory=memory,
            verbose=self.verbose,
            max_iterations=5,
            handle_parsing_errors=True
        )

