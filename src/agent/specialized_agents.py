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
from src.utils.logger import AgentLogger


class BaseSpecializedAgent:
    """专门Agent的基类"""
    
    def __init__(self, verbose: Optional[bool] = None):
        self.verbose = verbose if verbose is not None else config.get("agent.verbose", True)
        self.logger = AgentLogger(verbose=self.verbose)
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
            result = response.get("output", "抱歉，我无法处理您的请求。")
            return result
        except Exception as e:
            # 只记录错误，不重复输出（错误会在调用结束时记录）
            error_msg = str(e)
            # 简化错误信息，避免过长
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            raise Exception(error_msg)  # 重新抛出，让调用者处理


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
- **必须使用 get_weather_info 工具查询天气**，不要猜测或估算，不要直接回答
- **日期格式**：必须使用 YYYY-MM-DD 格式（例如：2026-01-21）
- **日期计算**：
  - 如果用户使用相对日期（如"今天"、"明天"、"3天后"），必须先计算具体日期
  - 计算相对日期时，必须以当前日期为基准
  - 使用 Python 的 datetime 逻辑：今天 + N天 = 目标日期
  - 确保年份正确（当前是2026年）
- **必须调用工具**：对于任何天气查询，都必须调用 get_weather_info 工具，即使遇到错误也要尝试
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
            verbose=False,  # 关闭LangChain的详细输出，使用我们自己的日志系统
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
2. **直接回答用户的问题，不要添加额外信息**
3. 对于自驾方式，使用高德地图API进行精确计算

**核心原则：简洁回答，只回答用户问的内容**

回答规则（必须严格遵守）：
- **如果用户只问了时间**（如"需要多久？"、"多久能到？"），**只回答时间**，格式：从[出发地]到[目的地]自驾大约需要[X]小时（[Y]分钟）。
- **如果用户只问了距离**（如"距离是多少？"、"有多远？"），**只回答距离**，格式：从[出发地]到[目的地]的距离是[X]公里。
- **如果用户问了详细规划**（如"帮我规划路线"、"详细路线"），才提供详细信息（距离、时间、费用、建议等）
- **绝对禁止**：不要提供用户没有询问的信息，包括但不限于：
  - 费用明细（除非用户明确询问）
  - 路线建议（除非用户明确询问）
  - 注意事项（除非用户明确询问）
  - 其他交通方式对比（除非用户明确询问）
  - 温馨提示（除非用户明确询问）

示例：
- 用户问："从北京到上海自驾需要多久？"
  正确回答："从北京到上海自驾大约需要14小时（837分钟）。"
  错误回答：不要提供距离、费用、建议等额外信息

- 用户问："北京到天津的距离是多少？"
  正确回答："从北京到天津的距离是136.7公里。"
  错误回答：不要提供时间、费用、建议等额外信息

必须使用 get_transport_route 工具查询路线，不要猜测或估算。回答要专业、准确、简洁，直接回答用户的问题，不要添加任何额外信息。"""
        
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
            verbose=False,  # 关闭LangChain的详细输出，使用我们自己的日志系统
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
            verbose=False,  # 关闭LangChain的详细输出，使用我们自己的日志系统
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
1. 使用 get_attraction_ticket_prices 工具查询景点门票价格和景点列表
2. 使用 answer_attraction_question 工具回答景点相关问题
3. 提供详细的景点信息，包括景点名称、地址、门票价格、人均消费等

重要原则：
- **必须使用工具查询信息**：收到查询后，立即调用相应的工具获取信息
- **返回完整的查询结果**：工具返回的信息必须完整地呈现给用户，不要只返回简短的确认信息
- **避免重复调用**：如果工具已经返回了完整信息，不要再重复调用相同的工具
- **整合信息**：如果查询了多个工具，将结果整合成完整的回复
- **详细描述**：对于景点列表，要清晰地列出所有查询到的景点信息，包括名称、地址、区域、人均消费等

回答格式：
- 查询景点列表时，直接返回工具查询到的景点信息，保持完整格式
- 回答景点问题时，直接返回工具查询到的答案
- 不要只回复"已查询"、"查询完成"等简短信息，必须返回完整的查询结果

回答要专业、准确、详细，确保信息完整。"""
        
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
            verbose=False,  # 关闭LangChain的详细输出，使用我们自己的日志系统
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
- **必须使用 plan_travel_itinerary 工具规划行程**，这是唯一可用的规划工具
- **优先使用已提供的查询信息**：如果输入中已经包含天气、交通、酒店、景点等信息，应该将这些信息作为 existing_* 参数传递给工具，避免重复查询
- **避免重复查询**：如果相关信息已经在输入中提供，不要让工具重新查询，直接使用提供的信息
- 提供详细、实用的行程安排
- 根据用户偏好和预算进行合理规划

**特别注意**：
- 工具支持 existing_weather_info、existing_transport_info、existing_hotel_info、existing_attraction_info 参数
- 如果输入中已经包含这些信息（通常在"已查询信息"部分），请将这些信息作为参数传递，避免重复查询
- 这样可以节省时间，提高效率

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
            verbose=False,  # 关闭LangChain的详细输出，使用我们自己的日志系统
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
            verbose=False,  # 关闭LangChain的详细输出，使用我们自己的日志系统
            max_iterations=5,
            handle_parsing_errors=True
        )

