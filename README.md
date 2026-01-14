# LLM-Travel-Assistant

基于LLM的智能旅行助手，支持自然语言行程规划、景点问答、个性化推荐，集成第三方API提供实时天气、交通、酒店和景点信息。

## 功能特性

- 🤖 **多Agent架构**：基于LangChain构建的智能多Agent系统，包含专门的天气、交通、酒店、景点、规划、推荐Agent
- 🌤️ **实时天气查询**：使用高德地图API获取目的地天气信息（支持4天预报和当天实况）
- 🏨 **酒店价格估算**：智能估算酒店价格，支持经济型、舒适型、豪华型、民宿、青旅等多种类型
- 🚗 **交通路线规划**：支持飞机、高铁、火车、自驾、大巴等多种出行方式，自驾使用高德地图API精准计算距离和时间
- 🎫 **景点门票查询**：使用天聚数行API或高德地图POI API查询景点信息和门票价格
- 🗺️ **行程规划**：根据目的地、天数、预算等自动生成详细行程，集成天气、酒店、交通、景点信息
- ❓ **景点问答**：回答关于景点的各种问题（开放时间、门票、最佳游览时间等）
- 🎯 **个性化推荐**：根据用户兴趣和旅行风格提供定制化推荐
- 💬 **对话记忆**：支持多轮对话，记住上下文信息
- 👤 **用户系统**：支持用户注册、登录，每个用户独立的会话
- 🌐 **Web界面**：现代化的聊天界面，支持实时对话和旅行信息表单，支持省市区三级联动选择
- 🧪 **单元测试**：完整的测试套件，包括工具测试、API连接测试、Agent初始化测试

## 项目结构

```
LLM-Travel-Assistant/
├── src/                      # 源代码目录
│   ├── agent/               # Agent核心模块
│   │   ├── travel_agent.py  # 旅行助手协调Agent（多Agent架构）
│   │   ├── specialized_agents.py  # 专门Agent（天气、交通、酒店、景点、规划、推荐）
│   │   └── tools.py         # Agent工具定义（天气、酒店、交通、景点）
│   ├── models/              # 数据模型
│   │   └── user.py         # 用户模型
│   ├── config.py            # 配置管理
│   └── main.py              # 命令行入口
├── templates/               # Web模板文件
│   ├── index.html          # 聊天界面模板（支持省市区三级联动）
│   ├── login.html          # 登录页面
│   └── register.html       # 注册页面
├── data/                    # 数据目录
│   └── users.json          # 用户数据（Git忽略）
├── tests/                   # 测试文件
│   ├── test_agent_tools.py  # 工具函数测试（使用mock）
│   ├── test_agent_api_connection.py  # API连接和功能测试（真实API）
│   ├── test_specialized_agents.py  # 专门Agent初始化测试
│   ├── run_all_tests.py    # 测试运行脚本
│   └── README.md            # 测试文档
├── scripts/                 # 工具脚本
├── docs/                    # 文档目录
├── app.py                   # Flask Web应用入口
├── config.yaml              # 配置文件
├── requirements.txt         # Python依赖
├── env.example              # 环境变量示例
└── README.md
```

详细结构说明请参考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 为 `.env` 或 `env` 并填入您的配置：

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
AMAP_API_KEY='your_amap_api_key_here'      # 高德地图（天气+交通）
TIANAPI_KEY='your_tianapi_key_here'         # 天聚数行（景点门票）
CTRIP_API_KEY='your_ctrip_api_key_here'     # 携程（酒店价格，需商业合作）
CTRIP_API_SECRET='your_ctrip_api_secret_here'
```

### 3. 运行程序

**方式1：Web界面（推荐）**

```bash
python app.py
```

然后在浏览器中访问：`http://127.0.0.1:5000`

首次使用需要注册账号，登录后即可使用。

**方式2：命令行界面**

```bash
python src/main.py
```

## 使用示例

### Web界面使用

1. **注册/登录**：首次使用需要注册账号
2. **填写旅行信息**：在左侧表单填写：
   - 出发日期和返回日期
   - 出发地和目的地
   - 预算
   - 旅店偏好（经济型/舒适型/豪华型/民宿/青旅）
   - 出行方式（飞机/高铁/火车/自驾/大巴）
   - 旅行风格（休闲游/深度游/探险游/文化游/美食游）
   - 兴趣偏好（如：历史、文化、美食）
3. **生成旅行计划**：点击"生成旅行计划"按钮，系统会自动查询天气、酒店、交通、景点信息并生成详细行程
4. **对话交互**：在输入框中输入问题，与助手进行多轮对话

### 命令行界面使用

```
您: 帮我规划一个3天的北京行程，预算5000元

您: 故宫的开放时间是什么？

您: 我喜欢历史和文化，推荐一些北京的景点
```

## API配置说明

### 必需配置

- **LLM API**：支持OpenAI API或兼容的API（如DeepSeek）
  - `OPENAI_API_KEY`：API密钥
  - `OPENAI_API_BASE`：API地址（默认：`https://api.openai.com/v1`）
  - `LLM_MODEL`：模型名称（默认：`gpt-4-turbo-preview`）

### 可选配置（不配置将使用智能估算）

- **高德地图API**（天气+交通）
  - 注册地址：https://lbs.amap.com/
  - 免费额度：每天30万次调用（个人开发者）
  - 环境变量：`AMAP_API_KEY`
  - 功能：天气查询（4天预报）、自驾路线规划

- **天聚数行API**（景点门票）
  - 注册地址：https://www.tianapi.com/
  - 免费额度：每天100次调用（个人开发者）
  - 环境变量：`TIANAPI_KEY`
  - 功能：景点门票价格查询

- **携程开放平台API**（酒店价格）
  - 注册地址：https://open.ctrip.com/
  - 注意：需要商业合作，当前使用智能估算方案
  - 环境变量：`CTRIP_API_KEY`、`CTRIP_API_SECRET`

## 配置说明

主要配置在 `config.yaml` 文件中：

- **LLM配置**：模型、温度、最大token数
- **Agent配置**：最大迭代次数、是否启用记忆
- **工具配置**：行程规划、景点问答、推荐等参数

## 测试

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

## 工具脚本

```bash
python scripts/example.py         # 运行使用示例
python scripts/test_api_connection.py  # 测试API连接
```

## 技术栈

- **LangChain**：Agent框架和工具链，支持多Agent架构
- **OpenAI API / DeepSeek API**：LLM服务
- **高德地图API**：天气查询（4天预报+实况）、路径规划（自驾路线精准计算）
- **天聚数行API**：景点门票查询
- **Flask**：Web框架
- **Python 3.8+**：开发语言
- **unittest**：单元测试框架

## 功能说明

### 天气查询
- 使用高德地图API获取实时天气和4天预报
- 超过4天的日期使用当前天气并给出估算提示
- 根据天气情况提供活动建议

### 酒店价格估算
- 基于城市、季节、酒店类型的智能估算
- 支持经济型、舒适型、豪华型、民宿、青旅等类型
- 考虑城市等级、旅游旺季/淡季等因素

### 交通路线规划
- **自驾**：使用高德地图API的地址编码和路线规划API，精准计算距离、时间、过路费
- **公共交通**：提供飞机、高铁、火车、大巴的票价和时间估算
- 所有方式都提供费用估算和路线建议

### 景点门票查询
- 优先使用天聚数行API获取门票价格
- 备选使用高德地图POI API获取景点信息
- 支持按兴趣偏好筛选景点

## 开发计划

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
- [ ] 支持更多LLM提供商（Claude、Gemini等）
- [ ] 对话历史保存
- [ ] 支持多语言
- [ ] 移动端适配

## 文档

- [快速开始指南](docs/QUICK_START.md)
- [运行指南](docs/RUN_GUIDE.md)
- [故障排除](docs/TROUBLESHOOTING.md)
- [项目结构说明](PROJECT_STRUCTURE.md)
- [项目概述](docs/PROJECT_OVERVIEW.md)

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 变更日志

### 2025-01-14 - 多Agent架构重构与测试完善

#### 🎯 架构重构
- ✅ **多Agent架构**：从单一Agent重构为协调Agent + 专门Agent的架构
  - 新增 `specialized_agents.py`，包含6个专门Agent：
    - `WeatherAgent`：专门负责天气查询服务
    - `TransportAgent`：专门负责交通路线规划服务
    - `HotelAgent`：专门负责酒店价格查询服务
    - `AttractionAgent`：专门负责景点信息查询服务
    - `PlanningAgent`：专门负责行程规划服务
    - `RecommendationAgent`：专门负责个性化推荐服务
  - `TravelAgent` 重构为主协调者，根据用户意图智能路由到相应的专门Agent

#### 🚀 功能增强
- ✅ **精准距离计算**：自驾场景下使用高德地图API的地址编码和路线规划API，精准计算距离和时间（不再使用估算）
- ✅ **省市区三级联动**：出发地和目的地支持省市区三级联动选择，提升用户体验
- ✅ **可选字段优化**：出发地和目的地改为可选，系统可根据用户偏好智能推荐目的地
- ✅ **默认值设置**：出发日期默认1.17，返回日期默认1.18，预算默认1000，出行方式默认自驾，旅行风格默认美食游

#### 🧪 测试完善
- ✅ **单元测试套件**：新增完整的测试框架
  - `test_agent_tools.py`：工具函数测试（使用mock，验证工具基本功能）
  - `test_agent_api_connection.py`：真实API连接和功能测试（验证API实际返回数据）
  - `test_specialized_agents.py`：专门Agent初始化测试
  - `run_all_tests.py`：一键运行所有测试
  - `tests/README.md`：测试文档说明

#### 🔧 代码优化
- ✅ **避免重复提交**：优化前端和后端逻辑，避免表单内容重复提交到后端
- ✅ **历史对话优化**：优化对话历史管理，避免冗余上下文
- ✅ **错误处理增强**：改进API调用失败时的降级处理
- ✅ **工具调用优化**：修复LangChain工具调用方式，统一使用字典参数

#### 📝 文档更新
- ✅ **README更新**：更新项目结构、功能特性、测试说明等
- ✅ **变更日志**：新增变更日志部分，记录时间线上的重要变更

### 2025-01-13 - API集成与功能优化

#### 🌐 第三方API集成
- ✅ **天气API**：从OpenWeatherMap切换到高德地图API，支持4天预报和当天实况
- ✅ **交通API**：集成高德地图API，支持自驾路线精准计算
- ✅ **景点API**：集成天聚数行API和高德地图POI API
- ✅ **酒店估算**：实现智能价格估算算法（携程API需商业合作，当前使用估算）

#### 🐛 Bug修复
- ✅ **登录重定向**：修复复制标签页刷新界面不会进入登录界面的问题
- ✅ **表单清空**：实现清空按钮的完整逻辑
- ✅ **距离计算**：修复行程规划时距离计算不准确的问题

### 2025-01-12 - 前端优化

#### 🎨 界面优化
- ✅ **表单优化**：移除"测试信息"按钮，优化表单交互
- ✅ **日期选择**：优化日期选择器体验
- ✅ **表单验证**：优化表单验证逻辑

### 2025-01-11 - 项目初始化

#### 🎉 初始版本
- ✅ **基础架构**：Flask Web应用、LangChain Agent框架
- ✅ **用户系统**：用户注册、登录功能
- ✅ **基础功能**：行程规划、景点问答、个性化推荐
- ✅ **Web界面**：现代化聊天界面

## 注意事项

1. **API密钥安全**：请勿将包含真实API密钥的 `env` 文件提交到代码仓库
2. **用户数据**：用户数据存储在 `data/users.json`，已配置Git忽略
3. **API限制**：注意各API的调用频率限制，合理使用
4. **估算数据**：当API不可用时，系统会使用智能估算，实际价格可能有所不同
