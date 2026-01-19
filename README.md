# LLM-Travel-Assistant

基于大语言模型（LLM）的智能旅行助手，支持自然语言行程规划、景点问答、个性化推荐，集成第三方API提供实时天气、交通、酒店和景点信息。

## ✨ 功能特性

### 🤖 多Agent架构
- **协调Agent**：`TravelAgent` 作为主协调者，智能路由用户请求到相应的专门Agent
- **专门Agent**：6个专门Agent各司其职
  - `WeatherAgent`：天气查询服务
  - `TransportAgent`：交通路线规划服务
  - `HotelAgent`：酒店价格查询服务
  - `AttractionAgent`：景点信息查询服务
  - `PlanningAgent`：行程规划服务
  - `RecommendationAgent`：个性化推荐服务

### 🌤️ 实时天气查询
- 使用高德地图API获取天气信息
- 支持4天天气预报和当天实况天气
- 超过4天的日期使用当前天气并给出估算提示
- 自动限流控制（每秒最多3次请求，最多3个并发）

### 🏨 酒店价格估算
- 智能估算酒店价格，基于城市、季节、酒店类型等因素
- 支持经济型、舒适型、豪华型、民宿、青旅等多种类型
- 考虑城市等级、旅游旺季/淡季等因素

### 🚗 交通路线规划
- **自驾**：使用高德地图API精准计算距离、时间、过路费、油费
- **公共交通**：提供飞机、高铁、火车、大巴的票价和时间估算
- 自动限流控制，避免API调用超限

### 🎫 景点门票查询
- 使用高德地图POI API查询景点信息
- 支持按兴趣偏好筛选景点
- 提供景点门票价格估算

### 🗺️ 智能行程规划
- 根据目的地、天数、预算等自动生成详细行程
- 自动整合天气、酒店、交通、景点信息
- 支持流式响应，实时显示规划进度

### ❓ 景点问答
- 回答关于景点的各种问题（开放时间、门票、最佳游览时间等）
- 基于实时API数据提供准确答案

### 🎯 个性化推荐
- 根据用户兴趣和旅行风格提供定制化推荐
- 支持历史、文化、美食、自然等多种兴趣偏好

### 💬 对话记忆
- 支持多轮对话，记住上下文信息
- 每个用户独立的会话管理

### 👤 用户系统
- 支持用户注册、登录
- 每个用户独立的Agent实例和对话历史

### 🌐 Web界面
- 现代化的聊天界面
- 支持实时对话和旅行信息表单
- 支持省市区三级联动选择
- 流式响应，实时显示工具执行进度

### 🧪 测试套件
- 完整的单元测试
- 工具函数测试（使用mock）
- API连接测试（真实API）
- Agent初始化测试

## 📁 项目结构

```
LLM-Travel-Assistant/
├── src/                          # 源代码目录
│   ├── agent/                    # Agent核心模块
│   │   ├── travel_agent.py      # 旅行助手协调Agent（多Agent架构）
│   │   ├── specialized_agents.py # 专门Agent（天气、交通、酒店、景点、规划、推荐）
│   │   └── tools.py             # Agent工具定义（天气、酒店、交通、景点）
│   ├── models/                   # 数据模型
│   │   └── user.py              # 用户模型
│   ├── utils/                    # 工具模块
│   │   ├── amap_rate_limiter.py # 高德地图API限流器
│   │   └── logger.py            # 日志记录器
│   ├── config.py                # 配置管理
│   └── main.py                  # 命令行入口
│
├── templates/                    # Web模板文件
│   ├── index.html               # 聊天界面模板（支持省市区三级联动）
│   ├── login.html               # 登录页面
│   └── register.html            # 注册页面
│
├── data/                        # 数据目录
│   └── users.json               # 用户数据（Git忽略）
│
├── tests/                       # 测试文件
│   ├── test_agent_tools.py     # 工具函数测试（使用mock）
│   ├── test_agent_api_connection.py  # API连接和功能测试（真实API）
│   ├── test_specialized_agents.py    # 专门Agent初始化测试
│   ├── run_all_tests.py        # 测试运行脚本
│   └── README.md               # 测试文档
│
├── scripts/                     # 工具脚本
│   ├── test_weather_api.py     # 天气API测试
│   ├── test_geocoding.py       # 地理编码测试
│   ├── test_driving_route.py   # 自驾路线测试
│   └── test_api_connection.py  # API连接测试
│
├── docs/                        # 文档目录
│   ├── PROJECT_OVERVIEW.md     # 项目概述
│   ├── QUICK_START.md          # 快速开始指南
│   ├── RUN_GUIDE.md            # 运行指南
│   └── TROUBLESHOOTING.md      # 故障排除
│
├── app.py                       # Flask Web应用入口
├── config.yaml                  # 配置文件
├── requirements.txt            # Python依赖
├── env.example                  # 环境变量示例
├── PROJECT_STRUCTURE.md        # 项目结构说明
├── LICENSE                     # 许可证
└── README.md                   # 项目说明
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
# 克隆项目（如果从Git仓库）
git clone <repository-url>
cd LLM-Travel-Assistant

# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `env.example` 为 `env` 并填入您的配置：

```bash
cp env.example env
```

编辑 `env` 文件，设置必要的API密钥：

```bash
# 必需：LLM API配置
OPENAI_API_KEY='your_openai_api_key_here'
OPENAI_API_BASE='https://api.deepseek.com/v1'  # 或使用OpenAI官方API
LLM_MODEL='deepseek-chat'  # 或 'gpt-4-turbo-preview'

# 可选：第三方API配置（不配置将使用智能估算）
# 高德地图API（同时用于天气、交通路线和景点查询）
AMAP_API_KEY='your_amap_api_key_here'
```

### 4. 运行程序

#### 方式1：Web界面（推荐）

```bash
python app.py
```

然后在浏览器中访问：`http://127.0.0.1:5000`

首次使用需要注册账号，登录后即可使用。

#### 方式2：命令行界面

```bash
python src/main.py
```

## 📖 使用指南

### Web界面使用

1. **注册/登录**
   - 首次使用需要注册账号
   - 登录后即可使用所有功能

2. **填写旅行信息**（可选）
   - 在左侧表单填写：
     - 出发日期和返回日期
     - 出发地和目的地（支持省市区三级联动）
     - 预算
     - 旅店偏好（经济型/舒适型/豪华型/民宿/青旅）
     - 出行方式（仅支持自驾）
     - 旅行风格（休闲游/深度游/探险游/文化游/美食游）
     - 兴趣偏好（如：历史、文化、美食）

3. **生成旅行计划**
   - 点击"生成旅行计划"按钮
   - 系统会自动查询天气、酒店、交通、景点信息
   - 实时显示工具执行进度
   - 生成详细的行程安排

4. **对话交互**
   - 在输入框中输入问题
   - 与助手进行多轮对话
   - 支持自然语言查询

### 命令行界面使用

```bash
python src/main.py
```

示例对话：

```
您: 帮我规划一个3天的北京行程，预算5000元

您: 北京明天天气怎么样？

您: 我喜欢历史和文化，推荐一些北京的景点
```

## ⚙️ API配置说明

### 必需配置

- **LLM API**：支持OpenAI API或兼容的API（如DeepSeek）
  - `OPENAI_API_KEY`：API密钥
  - `OPENAI_API_BASE`：API地址（默认：`https://api.openai.com/v1`）
  - `LLM_MODEL`：模型名称（默认：`gpt-4-turbo-preview`）

### 可选配置

- **高德地图API**（天气+交通+景点）
  - 注册地址：https://lbs.amap.com/
  - 免费额度：每天30万次调用（个人开发者）
  - 环境变量：`AMAP_API_KEY`
  - 功能：
    - 天气查询（4天预报+实况）
    - 自驾路线规划（精准计算距离、时间、费用）
    - 景点信息查询（POI搜索）
  - **限流控制**：自动限制每秒最多3次请求，最多3个并发

## 🔧 配置说明

主要配置在 `config.yaml` 文件中：

- **LLM配置**：模型、温度、最大token数
- **Agent配置**：最大迭代次数、是否启用记忆
- **工具配置**：行程规划、景点问答、推荐等参数

## 🧪 测试

### 运行所有测试

```bash
python tests/run_all_tests.py
```

### 运行特定测试

```bash
# 工具函数测试（使用mock，不依赖API）
python -m unittest tests.test_agent_tools

# API连接和功能测试（需要配置API密钥，测试真实API）
python -m unittest tests.test_agent_api_connection

# 专门Agent初始化测试
python -m unittest tests.test_specialized_agents
```

### 测试说明

- **test_agent_tools.py**：测试工具函数的基本功能，使用mock模拟API响应
- **test_agent_api_connection.py**：测试真实API连接和功能，验证API返回的实际数据
- **test_specialized_agents.py**：测试各个专门Agent的初始化和创建

详细测试文档请参考 [tests/README.md](tests/README.md)

## 🛠️ 技术栈

- **LangChain**：Agent框架和工具链，支持多Agent架构
- **OpenAI API / DeepSeek API**：LLM服务
- **高德地图API**：
  - 天气查询（4天预报+实况）
  - 路径规划（自驾路线精准计算）
  - 景点查询（POI搜索）
- **Flask**：Web框架
- **Python 3.8+**：开发语言
- **unittest**：单元测试框架

## 📚 功能详解

### 天气查询
- 使用高德地图API获取实时天气和4天预报
- 超过4天的日期使用当前天气并给出估算提示
- 自动限流控制，避免API调用超限

### 酒店价格估算
- 基于城市、季节、酒店类型的智能估算
- 支持经济型、舒适型、豪华型、民宿、青旅等类型
- 考虑城市等级、旅游旺季/淡季等因素

### 交通路线规划
- **自驾**：使用高德地图API的地址编码和路线规划API，精准计算距离、时间、过路费、油费
- 自动限流控制，确保API调用不超过限制

### 景点门票查询
- 使用高德地图POI API获取景点信息
- 支持按兴趣偏好筛选景点
- 提供门票价格估算

### 流式响应
- 支持Server-Sent Events (SSE)流式响应
- 实时显示工具执行进度
- 提升用户体验

## 📝 开发计划

- [x] Web界面开发
- [x] 项目目录整理
- [x] 用户登录系统
- [x] 实时天气查询功能
- [x] 交通路线规划（自驾精准计算）
- [x] 景点门票查询
- [x] 酒店价格估算
- [x] 多Agent架构重构
- [x] 单元测试套件
- [x] 省市区三级联动选择
- [x] 流式响应支持
- [x] API限流控制
- [ ] 支持更多LLM提供商（Claude、Gemini等）
- [ ] 对话历史保存
- [ ] 支持多语言
- [ ] 移动端适配

## 📄 文档

- [快速开始指南](docs/QUICK_START.md)
- [运行指南](docs/RUN_GUIDE.md)
- [故障排除](docs/TROUBLESHOOTING.md)
- [项目结构说明](PROJECT_STRUCTURE.md)
- [项目概述](docs/PROJECT_OVERVIEW.md)

## 📜 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## ⚠️ 注意事项

1. **API密钥安全**：请勿将包含真实API密钥的 `env` 文件提交到代码仓库
2. **用户数据**：用户数据存储在 `data/users.json`，已配置Git忽略
3. **API限制**：注意各API的调用频率限制，合理使用
4. **估算数据**：当API不可用时，系统会使用智能估算，实际价格可能有所不同
5. **限流控制**：高德地图API自动限流，每秒最多3次请求，最多3个并发

## 📅 变更日志

### 2025-01-15 - 代码优化与架构完善

#### 🔧 代码优化
- ✅ **工具函数优化**：移除工具层的活动建议逻辑，由Agent的LLM负责生成建议，符合职责分离原则
- ✅ **API限流优化**：完善高德地图API限流器，确保不超过每秒3次请求的限制

#### 📝 文档更新
- ✅ **README更新**：更新项目结构、功能特性、API配置说明等
- ✅ **项目整理**：整理项目目录结构，更新文档

### 2025-01-14 - 多Agent架构重构与测试完善

#### 🎯 架构重构
- ✅ **多Agent架构**：从单一Agent重构为协调Agent + 专门Agent的架构
  - 新增 `specialized_agents.py`，包含6个专门Agent
  - `TravelAgent` 重构为主协调者，根据用户意图智能路由到相应的专门Agent

#### 🚀 功能增强
- ✅ **精准距离计算**：自驾场景下使用高德地图API精准计算距离和时间
- ✅ **省市区三级联动**：出发地和目的地支持省市区三级联动选择
- ✅ **流式响应**：支持Server-Sent Events (SSE)流式响应，实时显示工具执行进度
- ✅ **API限流**：实现高德地图API并发限流器，避免API调用超限

#### 🧪 测试完善
- ✅ **单元测试套件**：新增完整的测试框架

### 2025-01-13 - API集成与功能优化

#### 🌐 第三方API集成
- ✅ **天气API**：从OpenWeatherMap切换到高德地图API，支持4天预报和当天实况
- ✅ **交通API**：集成高德地图API，支持自驾路线精准计算
- ✅ **景点API**：集成高德地图POI API

### 2025-01-12 - 前端优化

#### 🎨 界面优化
- ✅ **表单优化**：优化表单交互和验证逻辑
- ✅ **日期选择**：优化日期选择器体验

### 2025-01-11 - 项目初始化

#### 🎉 初始版本
- ✅ **基础架构**：Flask Web应用、LangChain Agent框架
- ✅ **用户系统**：用户注册、登录功能
- ✅ **基础功能**：行程规划、景点问答、个性化推荐
- ✅ **Web界面**：现代化聊天界面
