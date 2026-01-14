"""智能旅行助手Agent - 主协调Agent"""
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import Tool
from src.agent.tools import TRAVEL_TOOLS
from src.agent.specialized_agents import (
    WeatherAgent,
    TransportAgent,
    HotelAgent,
    AttractionAgent,
    PlanningAgent,
    RecommendationAgent
)
from src.config import config


class TravelAgent:
    """智能旅行助手Agent类"""
    
    def __init__(self, enable_memory: Optional[bool] = None, verbose: Optional[bool] = None, session_id: Optional[str] = None):
        self.enable_memory = enable_memory if enable_memory is not None else config.get("agent.enable_memory", True)
        self.verbose = verbose if verbose is not None else config.get("agent.verbose", True)
        self.session_id = session_id  # 用于区分不同用户的偏好
        
        # 存储旅行信息
        self.travel_info = {}
        # 跟踪旅行信息是否已经添加到对话中（避免重复添加）
        self.travel_info_added_to_conversation = False
        self.last_travel_info_hash = None
        
        # 初始化专门的Agent实例
        if self.verbose:
            print("初始化专门的Agent...", flush=True)
        self.weather_agent = WeatherAgent(verbose=self.verbose)
        self.transport_agent = TransportAgent(verbose=self.verbose)
        self.hotel_agent = HotelAgent(verbose=self.verbose)
        self.attraction_agent = AttractionAgent(verbose=self.verbose)
        self.planning_agent = PlanningAgent(verbose=self.verbose)
        self.recommendation_agent = RecommendationAgent(verbose=self.verbose)
        if self.verbose:
            print("所有专门Agent初始化完成", flush=True)
        
        # 初始化LLM
        import os
        
        # 设置环境变量（ChatOpenAI 会从环境变量读取）
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY 未设置，请在 env 文件中配置API密钥")
        
        os.environ["OPENAI_API_KEY"] = config.openai_api_key
        
        # 构建参数字典，只传递基本参数
        llm_kwargs = {
            "model": config.llm_model,
            "temperature": config.get("llm.temperature", 0.7),
            "openai_api_key": config.openai_api_key,
            "timeout": 60,  # 设置60秒超时
            "max_retries": 2,  # 最多重试2次
        }
        
        # 如果API base不是OpenAI默认值，需要设置
        if config.openai_api_base and "openai.com" not in config.openai_api_base:
            os.environ["OPENAI_API_BASE"] = config.openai_api_base
            llm_kwargs["openai_api_base"] = config.openai_api_base
        
        # 添加 max_tokens（如果支持）
        max_tokens = config.get("llm.max_tokens", 2000)
        if max_tokens:
            llm_kwargs["max_tokens"] = max_tokens
        
        try:
            self.llm = ChatOpenAI(**llm_kwargs)
            # 测试LLM是否可用（可选，但会增加初始化时间）
            if self.verbose:
                print("LLM初始化成功", flush=True)
        except Exception as e:
            error_msg = str(e)
            if self.verbose:
                print(f"LLM初始化失败: {error_msg}", flush=True)
            raise ValueError(
                f"LLM初始化失败: {error_msg}\n"
                f"请检查：\n"
                f"1. API密钥是否正确（当前: {config.openai_api_key[:10]}...）\n"
                f"2. API地址是否正确（当前: {config.openai_api_base}）\n"
                f"3. 模型名称是否正确（当前: {config.llm_model}）\n"
                f"4. 网络连接是否正常"
            )
        
        # 创建Agent
        self.agent_executor = self._create_agent()
    
    def _create_agent(self):
        """创建主协调Agent执行器"""
        # 创建调用专门Agent的工具
        agent_tools = self._create_agent_tools()
        
        # 系统提示词
        system_prompt = """你是一个专业的智能旅行助手主协调者，负责理解用户需求并调用相应的专门Agent来完成任务。

你的职责：
1. **理解用户意图**：分析用户的问题，判断需要调用哪个专门Agent
2. **协调专门Agent**：根据用户需求调用相应的专门Agent：
   - 天气查询 → 调用 query_weather_agent
   - 交通路线 → 调用 query_transport_agent
   - 酒店价格 → 调用 query_hotel_agent
   - 景点信息 → 调用 query_attraction_agent
   - 行程规划 → 调用 query_planning_agent
   - 个性化推荐 → 调用 query_recommendation_agent
3. **整合信息**：将各个专门Agent的回复整合成完整的回答

可用的专门Agent：
- **天气Agent** (query_weather_agent)：专门负责天气查询，使用高德地图API获取准确天气信息
- **交通Agent** (query_transport_agent)：专门负责交通路线规划，使用高德地图API精确计算自驾距离和时间
- **酒店Agent** (query_hotel_agent)：专门负责酒店价格查询，提供准确的预算估算
- **景点Agent** (query_attraction_agent)：专门负责景点信息查询和问答
- **规划Agent** (query_planning_agent)：专门负责行程规划，整合所有信息生成详细行程
- **推荐Agent** (query_recommendation_agent)：专门负责个性化推荐

重要原则：
- **理解用户需求**：仔细分析用户提供的旅行信息，包括出发日期、返回日期、出发地（可选）、目的地（可选）、预算、旅店偏好、出行方式、旅行风格和兴趣偏好等
- **灵活处理可选信息**：出发地和目的地都是可选的。如果用户未提供目的地，应根据用户的偏好、预算和旅行天数推荐合适的目的地
- **智能路由**：根据用户问题类型，调用相应的专门Agent：
  - 天气相关问题 → query_weather_agent
  - 交通路线问题 → query_transport_agent
  - 酒店价格问题 → query_hotel_agent
  - 景点相关问题 → query_attraction_agent
  - 行程规划需求 → query_planning_agent
  - 推荐需求 → query_recommendation_agent
- **综合查询**：当用户需要规划完整行程时，应该：
  1. 先调用 query_transport_agent 查询交通路线（如果有出发地和目的地）
  2. 调用 query_weather_agent 查询天气（如果有日期和目的地）
  3. 调用 query_hotel_agent 查询酒店价格（如果有日期、目的地和酒店偏好）
  4. 调用 query_attraction_agent 查询景点信息（如果有目的地和兴趣偏好）
  5. 最后调用 query_planning_agent 整合所有信息生成详细行程
- **个性化服务**：所有建议都应考虑用户的偏好和需求，提供真正个性化的服务
- **专业详细**：提供详细、准确、实用的旅行建议，结合实时天气和价格信息

特别注意：
- 用户可能会提供旅行信息（格式为【用户旅行信息】），包括出发日期、返回日期、出发地（可选）、目的地（可选）、预算、旅店偏好、出行方式、旅行风格和兴趣偏好等
- **在规划行程前，应该按顺序调用相应的专门Agent查询信息**（如果相关信息可用）
- **重要**：对于自驾方式，交通Agent会使用高德地图API精确计算距离和时间，确保使用实际数据而不是估算
- 如果用户未指定目的地，应根据用户的偏好、预算、旅行天数和兴趣推荐合适的目的地
- 根据天气情况调整活动建议（如雨天推荐室内活动，晴天推荐户外活动）
- 根据酒店价格、交通费用、景点门票信息调整预算分配，提供更准确的费用估算

回答要友好、专业、详细，并体现对用户需求的理解和应用。"""
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建Agent（使用专门Agent工具）
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=agent_tools,
            prompt=prompt
        )
        
        # 创建内存（如果启用）
        memory = None
        if self.enable_memory:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        
        # 创建Agent执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=agent_tools,
            memory=memory,
            verbose=self.verbose,
            max_iterations=config.get("agent.max_iterations", 15),  # 增加迭代次数，因为需要调用多个agent
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def _create_agent_tools(self):
        """创建调用专门Agent的工具"""
        tools = []
        
        # 天气Agent工具
        tools.append(Tool(
            name="query_weather_agent",
            func=lambda query: self.weather_agent.query(query),
            description="查询天气信息的专门Agent。当用户询问天气、需要根据天气调整行程时使用。输入应该包含城市名称和日期。"
        ))
        
        # 交通Agent工具
        tools.append(Tool(
            name="query_transport_agent",
            func=lambda query: self.transport_agent.query(query),
            description="查询交通路线信息的专门Agent。当用户询问交通路线、距离、时间、费用时使用。对于自驾方式，会使用高德地图API精确计算。输入应该包含出发地、目的地和出行方式。"
        ))
        
        # 酒店Agent工具
        tools.append(Tool(
            name="query_hotel_agent",
            func=lambda query: self.hotel_agent.query(query),
            description="查询酒店价格信息的专门Agent。当用户询问酒店价格、住宿预算时使用。输入应该包含城市、入住日期、退房日期和酒店偏好。"
        ))
        
        # 景点Agent工具
        tools.append(Tool(
            name="query_attraction_agent",
            func=lambda query: self.attraction_agent.query(query),
            description="查询景点信息的专门Agent。当用户询问景点门票、景点信息、景点问答时使用。输入应该包含城市、景点名称或兴趣偏好。"
        ))
        
        # 规划Agent工具
        tools.append(Tool(
            name="query_planning_agent",
            func=lambda query: self.planning_agent.query(query),
            description="规划旅行行程的专门Agent。当用户需要规划详细行程时使用。该Agent会整合天气、酒店、交通、景点等信息。输入应该包含旅行天数、目的地、预算、偏好等信息。"
        ))
        
        # 推荐Agent工具
        tools.append(Tool(
            name="query_recommendation_agent",
            func=lambda query: self.recommendation_agent.query(query),
            description="提供个性化推荐的专门Agent。当用户需要推荐目的地、景点、活动时使用。输入应该包含目的地、兴趣偏好、旅行风格等信息。"
        ))
        
        return tools
    
    def chat(self, user_input: str) -> str:
        """
        与用户对话
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent的回复
        """
        try:
            # 检查旅行信息是否变化
            import hashlib
            travel_info_str = str(sorted(self.travel_info.items()))
            current_travel_info_hash = hashlib.md5(travel_info_str.encode()).hexdigest()
            
            # 如果旅行信息变化了，或者还没有添加到对话中，则添加
            # 否则直接使用用户输入，避免重复添加旅行信息
            if self.travel_info and (not self.travel_info_added_to_conversation or current_travel_info_hash != self.last_travel_info_hash):
                travel_context = self._format_travel_info()
                combined_input = f"{travel_context}\n\n用户问题: {user_input}"
                self.travel_info_added_to_conversation = True
                self.last_travel_info_hash = current_travel_info_hash
            else:
                # 旅行信息已经添加过且未变化，直接使用用户输入
                # ConversationBufferMemory会自动管理历史对话
                combined_input = user_input
            
            if self.verbose:
                print(f"Agent输入: {combined_input[:200]}...", flush=True)
            
            # 调用Agent执行器（ConversationBufferMemory会自动包含历史对话）
            response = self.agent_executor.invoke({"input": combined_input})
            output = response.get("output", "抱歉，我无法处理您的请求。")
            
            if self.verbose:
                print(f"Agent输出长度: {len(output)}", flush=True)
            
            # 检查输出是否包含错误信息
            if "错误" in output or "error" in output.lower() or "❌" in output:
                # 提供更详细的错误诊断
                error_lower = output.lower()
                if "connection" in error_lower or "connect" in error_lower:
                    return "❌ 连接错误：无法连接到AI服务。\n\n可能的原因：\n1. API密钥未配置或配置错误\n2. 网络连接问题\n3. API服务暂时不可用\n\n请检查您的API配置和网络连接。"
                elif "api" in error_lower and "key" in error_lower:
                    return "❌ API密钥错误：请检查您的API密钥是否正确配置。\n\n请在 env 文件中设置正确的 OPENAI_API_KEY。"
                elif "rate limit" in error_lower or "quota" in error_lower:
                    return "❌ API配额不足：您的API调用次数已用完或达到限制。\n\n请检查您的API账户余额或等待限制重置。"
            
            return output
        except Exception as e:
            import traceback
            error_str = str(e).lower()
            error_trace = traceback.format_exc()
            
            if self.verbose:
                print(f"Agent执行错误: {e}", flush=True)
                print(f"错误堆栈:\n{error_trace}", flush=True)
            
            # 根据错误类型提供友好的错误信息
            if "connection" in error_str or "connect" in error_str:
                return "❌ 连接错误：无法连接到AI服务。\n\n请检查：\n1. 网络连接是否正常\n2. API服务地址是否正确\n3. 防火墙或代理设置\n\n详细错误: " + str(e)
            elif "api" in error_str and ("key" in error_str or "auth" in error_str):
                return "❌ 认证错误：API密钥无效或未配置。\n\n请在 env 文件中设置正确的 OPENAI_API_KEY。\n\n详细错误: " + str(e)
            elif "timeout" in error_str:
                return "❌ 请求超时：AI服务响应时间过长。\n\n请稍后重试，或检查网络连接。\n\n详细错误: " + str(e)
            else:
                return f"❌ 处理您的请求时出现错误: {str(e)}\n\n如果问题持续，请检查API配置和网络连接。\n\n错误类型: {type(e).__name__}"
    
    def _format_travel_info(self) -> str:
        """
        将旅行信息格式化为可读的上下文
        
        Returns:
            格式化后的旅行信息字符串
        """
        if not self.travel_info:
            return ""
        
        formatted_info = "【用户旅行信息】"
        
        # 定义需要显示的字段及其中文名称
        fields = [
            ("departureDate", "出发日期"),
            ("returnDate", "返回日期"),
            ("departureCity", "出发地"),
            ("destination", "目的地"),
            ("budget", "预算"),
            ("hotelPreference", "旅店偏好"),
            ("transportMode", "出行方式"),
            ("travelStyle", "旅行风格"),
            ("interests", "兴趣偏好")
        ]
        
        for field, chinese_name in fields:
            value = self.travel_info.get(field, "")
            if value:
                formatted_info += f"\n{chinese_name}: {value}"
        
        # 添加提示，让Agent知道要查询天气和酒店价格
        if self.travel_info.get("departureDate") and self.travel_info.get("destination"):
            formatted_info += "\n\n[重要提示：请使用 get_weather_info 工具查询出发日期的天气信息]"
        
        if self.travel_info.get("departureDate") and self.travel_info.get("returnDate") and self.travel_info.get("hotelPreference"):
            formatted_info += "\n[重要提示：请使用 get_hotel_prices 工具查询酒店价格信息]"
        
        return formatted_info
    
    def set_travel_info(self, travel_info: dict):
        """
        设置旅行信息
        
        Args:
            travel_info: 包含旅行偏好的字典，如出发日期、返回日期、目的地等
        """
        if travel_info:
            # 检查旅行信息是否真的变化了
            import hashlib
            old_hash = hashlib.md5(str(sorted(self.travel_info.items())).encode()).hexdigest()
            new_hash = hashlib.md5(str(sorted(travel_info.items())).encode()).hexdigest()
            
            self.travel_info = travel_info
            
            # 如果旅行信息变化了，重置标志，下次对话时会重新添加
            if old_hash != new_hash:
                self.travel_info_added_to_conversation = False
    
    def get_travel_info(self) -> dict:
        """
        获取当前存储的旅行信息
        
        Returns:
            旅行信息字典
        """
        return self.travel_info
    
    def reset_memory(self):
        """重置对话记忆和旅行信息"""
        if self.agent_executor.memory:
            self.agent_executor.memory.clear()
        # 重置旅行信息
        self.travel_info = {}
        self.travel_info_added_to_conversation = False
        self.last_travel_info_hash = None

