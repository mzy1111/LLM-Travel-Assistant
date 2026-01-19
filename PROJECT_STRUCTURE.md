# 项目目录结构

```
LLM-Travel-Assistant/
├── src/                          # 源代码目录
│   ├── agent/                    # Agent核心模块
│   │   ├── __init__.py          # 模块初始化
│   │   ├── travel_agent.py      # 旅行助手协调Agent（多Agent架构）
│   │   ├── specialized_agents.py # 专门Agent（天气、交通、酒店、景点、规划、推荐）
│   │   └── tools.py             # Agent工具定义（天气、酒店、交通、景点）
│   ├── models/                   # 数据模型
│   │   └── user.py              # 用户模型
│   ├── utils/                    # 工具模块
│   │   ├── __init__.py          # 模块初始化
│   │   ├── amap_rate_limiter.py # 高德地图API限流器
│   │   └── logger.py            # 日志记录器
│   ├── __init__.py               # 模块初始化
│   ├── config.py                # 配置管理
│   └── main.py                  # 命令行入口
│
├── templates/                    # Web模板文件
│   ├── index.html               # 聊天界面模板（支持省市区三级联动、流式响应）
│   ├── login.html               # 登录页面
│   └── register.html            # 注册页面
│
├── data/                        # 数据目录
│   └── users.json               # 用户数据（Git忽略）
│
├── tests/                       # 测试文件
│   ├── __init__.py             # 模块初始化
│   ├── test_agent_tools.py     # 工具函数测试（使用mock）
│   ├── test_agent_api_connection.py  # API连接和功能测试（真实API）
│   ├── test_specialized_agents.py    # 专门Agent初始化测试
│   ├── test_config.py          # 配置测试
│   ├── test_import.py          # 导入测试
│   ├── run_all_tests.py        # 测试运行脚本
│   └── README.md               # 测试文档
│
├── scripts/                     # 工具脚本
│   ├── __init__.py             # 模块初始化
│   ├── example.py              # 使用示例
│   ├── test_api_connection.py  # API连接测试
│   ├── test_weather_api.py    # 天气API测试
│   ├── test_geocoding.py      # 地理编码测试
│   └── test_driving_route.py  # 自驾路线测试
│
├── docs/                        # 文档目录
│   ├── PROJECT_OVERVIEW.md     # 项目概述
│   ├── QUICK_START.md          # 快速开始指南
│   ├── RUN_GUIDE.md            # 运行指南
│   ├── TROUBLESHOOTING.md      # 故障排除
│   └── README.md               # 文档说明
│
├── .vscode/                     # VS Code配置
│   └── launch.json             # 调试配置
│
├── app.py                       # Flask Web应用入口
├── config.yaml                  # 配置文件
├── requirements.txt            # Python依赖
├── env.example                  # 环境变量示例
├── env                          # 环境变量（Git忽略，不提交）
├── PROJECT_STRUCTURE.md        # 项目结构说明（本文件）
├── 调试说明.md                  # 调试指南
├── LICENSE                     # 许可证
└── README.md                   # 项目说明
```

## 目录说明

### src/
核心源代码目录，包含所有业务逻辑。

- `agent/`: Agent核心模块
  - `travel_agent.py`: 旅行助手协调Agent，作为主协调者，智能路由用户请求
  - `specialized_agents.py`: 6个专门Agent，各司其职
    - `WeatherAgent`: 天气查询服务
    - `TransportAgent`: 交通路线规划服务
    - `HotelAgent`: 酒店价格查询服务
    - `AttractionAgent`: 景点信息查询服务
    - `PlanningAgent`: 行程规划服务
    - `RecommendationAgent`: 个性化推荐服务
  - `tools.py`: Agent工具定义，包含所有可用的工具函数
- `models/`: 数据模型
  - `user.py`: 用户模型，管理用户注册、登录、数据存储
- `utils/`: 工具模块
  - `amap_rate_limiter.py`: 高德地图API限流器，控制API调用频率
  - `logger.py`: 日志记录器，统一日志格式
- `config.py`: 配置管理，加载环境变量和配置文件
- `main.py`: 命令行入口，用于命令行交互模式

### templates/
Web界面模板文件，使用Flask渲染。

- `index.html`: 主聊天界面，包含：
  - 旅行信息表单（支持省市区三级联动）
  - 对话区域（支持流式响应）
  - 实时工具执行进度显示
- `login.html`: 用户登录页面
- `register.html`: 用户注册页面

### data/
数据存储目录，包括用户数据。

- `users.json`: 用户数据文件（Git忽略，不提交到仓库）

### tests/
测试文件目录，用于单元测试和集成测试。

- `test_agent_tools.py`: 工具函数测试（使用mock，验证工具基本功能）
- `test_agent_api_connection.py`: 真实API连接和功能测试（验证API实际返回数据）
- `test_specialized_agents.py`: 专门Agent初始化测试
- `test_config.py`: 配置测试
- `test_import.py`: 导入测试
- `run_all_tests.py`: 一键运行所有测试
- `README.md`: 测试文档说明

### scripts/
工具脚本目录，包含辅助脚本和示例代码。

- `example.py`: 使用示例
- `test_api_connection.py`: API连接测试
- `test_weather_api.py`: 天气API测试
- `test_geocoding.py`: 地理编码测试
- `test_driving_route.py`: 自驾路线测试

### docs/
文档目录，包含项目文档和使用指南。

- `PROJECT_OVERVIEW.md`: 项目概述
- `QUICK_START.md`: 快速开始指南
- `RUN_GUIDE.md`: 运行指南
- `TROUBLESHOOTING.md`: 故障排除
- `README.md`: 文档说明

### .vscode/
VS Code配置目录。

- `launch.json`: 调试配置文件，包含多个调试配置

## 运行说明

### Web界面
```bash
python app.py
```
访问 http://127.0.0.1:5000

### 命令行界面
```bash
python src/main.py
```

### 运行测试
```bash
# 运行所有测试
python tests/run_all_tests.py

# 运行特定测试
python -m unittest tests.test_agent_tools
python -m unittest tests.test_agent_api_connection
python -m unittest tests.test_specialized_agents
```

### 工具脚本
```bash
python scripts/example.py
python scripts/test_api_connection.py
python scripts/test_weather_api.py
python scripts/test_geocoding.py
python scripts/test_driving_route.py
```

## 架构说明

### 多Agent架构

```
用户请求
    ↓
TravelAgent (协调Agent)
    ↓
┌─────────────────────────────────────┐
│  根据用户意图路由到相应的专门Agent    │
│  - WeatherAgent (天气查询)          │
│  - TransportAgent (交通路线)       │
│  - HotelAgent (酒店价格)            │
│  - AttractionAgent (景点信息)       │
│  - PlanningAgent (行程规划)         │
│  - RecommendationAgent (个性化推荐) │
└─────────────────────────────────────┘
    ↓
专门Agent调用工具函数
    ↓
第三方API (高德地图等)
    ↓
返回结果给用户
```

### 工具调用流程

```
专门Agent
    ↓
调用工具函数 (tools.py)
    ↓
API限流器 (amap_rate_limiter.py)
    ↓
第三方API
    ↓
返回结果
```

### 流式响应流程

```
用户请求
    ↓
Flask SSE端点 (/api/chat/stream)
    ↓
Agent执行（在独立线程中）
    ↓
工具执行回调 (ToolCallbackHandler)
    ↓
实时推送更新到前端
    ↓
前端实时显示进度
```

## 关键文件说明

### app.py
Flask Web应用入口，包含：
- 路由定义（登录、注册、聊天、行程规划等）
- 流式响应端点（SSE）
- Agent实例管理
- 会话管理

### config.yaml
应用配置文件，包含：
- LLM配置（模型、温度、最大token数）
- Agent配置（最大迭代次数、是否启用记忆）
- 工具配置（行程规划、景点问答、推荐等参数）

### env.example
环境变量示例文件，包含：
- LLM API配置（必需）
- 第三方API配置（可选）

### requirements.txt
Python依赖列表，包含：
- LangChain相关包
- Flask
- 数据处理库
- 工具库

## 注意事项

1. **环境变量**：`env` 文件包含敏感信息，已配置Git忽略，不要提交到仓库
2. **用户数据**：`data/users.json` 包含用户信息，已配置Git忽略
3. **缓存文件**：`__pycache__` 目录包含Python缓存文件，已配置Git忽略
4. **API密钥**：所有API密钥都应在 `env` 文件中配置，不要硬编码在代码中
