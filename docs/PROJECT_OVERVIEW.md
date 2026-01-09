# 项目理解文档

## 项目概述

**LLM-Travel-Assistant** 是一个基于大语言模型（LLM）的智能旅行助手系统，使用 LangChain Agent 框架和 RAG（检索增强生成）技术，帮助用户规划旅行行程、回答景点问题、提供个性化推荐。

## 核心架构

### 1. 技术栈

- **后端框架**: Flask (Web服务)
- **LLM框架**: LangChain
- **LLM提供商**: OpenAI API (支持 DeepSeek 等兼容API)
- **向量数据库**: ChromaDB
- **嵌入模型**: 
  - 优先使用 sentence-transformers (本地)
  - 备选：简单文本匹配模式（网络受限时）
- **Python版本**: 3.8+

### 2. 系统架构

```
用户请求
    ↓
Flask Web应用 (app.py)
    ↓
TravelAgent (智能Agent)
    ↓
┌─────────────────┬──────────────────┐
│   Agent工具      │   RAG知识库      │
│   - 行程规划     │   - 向量检索     │
│   - 景点问答     │   - 文档加载     │
│   - 个性化推荐   │   - 相似度搜索   │
└─────────────────┴──────────────────┘
    ↓
LLM (OpenAI/DeepSeek)
    ↓
返回结果给用户
```

## 核心模块详解

### 1. Agent 模块 (`src/agent/`)

#### TravelAgent (`travel_agent.py`)
- **功能**: 智能对话Agent，协调所有工具和知识库
- **特性**:
  - 多轮对话记忆（ConversationBufferMemory）
  - 旅行信息管理（出发日期、目的地、预算等）
  - 自动工具选择和执行
- **工作流程**:
  1. 接收用户输入
  2. 如果有旅行信息，将其作为上下文
  3. 选择合适的工具（搜索知识库、规划行程等）
  4. 调用LLM生成回复
  5. 返回结果

#### Tools (`tools.py`)
定义了4个核心工具：

1. **search_travel_knowledge**: 搜索旅行知识库
   - 输入: 查询字符串
   - 输出: 相关文档内容

2. **plan_travel_itinerary**: 规划旅行行程
   - 输入: 目的地、天数、预算、偏好
   - 输出: 详细行程规划提示

3. **answer_attraction_question**: 回答景点问题
   - 输入: 问题、景点名称（可选）
   - 输出: 基于知识库的答案

4. **get_personalized_recommendations**: 个性化推荐
   - 输入: 目的地、兴趣、旅行风格
   - 输出: 个性化推荐列表

### 2. 知识库模块 (`src/knowledge_base/`)

#### VectorStore (`vector_store.py`)
- **功能**: 管理向量数据库，提供相似度搜索
- **嵌入模型策略**:
  1. 优先尝试本地 sentence-transformers（离线模式）
  2. 如果失败，尝试在线下载
  3. 如果网络问题，使用简单文本匹配模式
- **特性**:
  - 延迟初始化（避免启动时阻塞）
  - 自动回退机制
  - 支持文档添加和检索

#### DocumentLoader (`loader.py`)
- **功能**: 加载知识库文档
- **支持格式**: txt, pdf, csv, json
- **方法**:
  - `load_file()`: 加载单个文件
  - `load_directory()`: 加载目录下所有文件
  - `load_knowledge_base()`: 加载知识库目录

### 3. 配置模块 (`src/config.py`)

- **功能**: 统一管理配置
- **配置来源**:
  1. 环境变量 (.env 或 env 文件)
  2. YAML配置文件 (config.yaml)
- **配置项**:
  - API密钥和基础URL
  - LLM模型配置
  - 嵌入模型配置
  - RAG参数
  - Agent参数

### 4. Web应用 (`app.py`)

#### 路由设计
- `GET /`: 主页（聊天界面）
- `GET /chat`: 聊天页面
- `GET /plan`: 行程规划页面
- `POST /api/chat`: 处理聊天请求
- `POST /api/reset`: 重置对话
- `GET /api/status`: 获取系统状态

#### 会话管理
- 使用 Flask session 存储会话ID
- 每个会话维护独立的 Agent 实例
- 支持旅行信息持久化

## 数据流

### 用户对话流程

```
1. 用户在Web界面填写旅行信息（可选）
   ↓
2. 用户输入问题
   ↓
3. 前端发送请求到 /api/chat
   ↓
4. Flask接收请求，获取或创建Agent
   ↓
5. 如果有旅行信息，传递给Agent
   ↓
6. Agent处理用户输入：
   - 分析用户意图
   - 选择合适的工具
   - 从知识库检索相关信息
   - 调用LLM生成回复
   ↓
7. 返回结果给前端
   ↓
8. 前端显示回复
```

### 知识库检索流程

```
1. 用户问题 → Agent
   ↓
2. Agent调用 search_travel_knowledge 工具
   ↓
3. 工具将问题转换为向量查询
   ↓
4. VectorStore执行相似度搜索
   ↓
5. 返回Top-K相关文档
   ↓
6. 文档内容作为上下文传递给LLM
   ↓
7. LLM基于上下文生成回答
```

## 关键特性

### 1. RAG (检索增强生成)
- **目的**: 解决LLM幻觉问题，提供准确信息
- **实现**: 
  - 文档向量化存储
  - 语义相似度搜索
  - 检索结果作为上下文

### 2. Agent框架
- **目的**: 让LLM能够使用工具，执行复杂任务
- **实现**:
  - LangChain AgentExecutor
  - 工具自动选择
  - 多步骤推理

### 3. 多轮对话
- **目的**: 保持上下文，提供连贯对话
- **实现**:
  - ConversationBufferMemory
  - 会话级别的Agent实例

### 4. 旅行信息管理
- **目的**: 个性化行程规划
- **实现**:
  - 前端表单收集信息
  - Agent存储和使用旅行信息
  - 自动整合到对话上下文

## 文件结构说明

```
src/
├── agent/
│   ├── travel_agent.py  # Agent核心类，协调工具和LLM
│   └── tools.py         # Agent可用的工具定义
├── knowledge_base/
│   ├── vector_store.py  # 向量数据库管理
│   └── loader.py       # 文档加载器
├── config.py            # 配置管理
└── main.py              # 命令行入口

app.py                   # Flask Web应用入口
templates/
└── index.html          # Web界面模板

data/
├── knowledge_base/      # 知识库文档（txt/pdf/csv/json）
└── chroma_db/          # 向量数据库存储
```

## 工作流程示例

### 场景1: 规划行程

```
用户: "帮我规划一个3天的北京行程，预算5000元"

1. Agent接收请求
2. 识别需要调用 plan_travel_itinerary 工具
3. 工具先调用 search_travel_knowledge 搜索"北京 景点 推荐"
4. 获取知识库中的北京景点信息
5. 将信息传递给LLM，生成详细行程
6. 返回给用户
```

### 场景2: 景点问答

```
用户: "故宫的开放时间是什么？"

1. Agent接收请求
2. 识别需要调用 answer_attraction_question 工具
3. 工具搜索"故宫 开放时间"
4. 从知识库检索相关信息
5. 返回答案
```

## 配置要点

### 环境变量 (env 或 .env)
- `OPENAI_API_KEY`: API密钥
- `OPENAI_API_BASE`: API基础URL（如使用DeepSeek）
- `LLM_MODEL`: LLM模型名称
- `EMBEDDING_MODEL`: 嵌入模型名称

### 配置文件 (config.yaml)
- LLM参数（温度、最大token）
- 嵌入模型配置
- RAG参数（检索数量、相似度阈值）
- Agent参数（最大迭代次数、是否启用记忆）

## 扩展方向

1. **更多LLM支持**: Claude、Gemini等
2. **实时数据**: 天气、交通、价格
3. **地图集成**: 路线规划、位置展示
4. **多语言支持**: 国际化
5. **历史记录**: 保存对话和行程
6. **用户系统**: 登录、个人偏好

## 常见问题

### Q: 为什么使用RAG而不是直接让LLM回答？
A: RAG可以确保信息准确性，减少幻觉，特别是对于具体的景点信息、开放时间等事实性内容。

### Q: Agent如何选择使用哪个工具？
A: LLM根据用户问题和可用工具的描述，自动选择最合适的工具。LangChain的Agent框架负责这个决策过程。

### Q: 旅行信息如何影响回复？
A: 旅行信息会被格式化为上下文，添加到用户问题前，让LLM在生成回复时考虑这些信息。

