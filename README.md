# LLM-Travel-Assistant

基于LLM的智能旅行助手，支持自然语言行程规划、景点问答、个性化推荐，集成第三方API提供实时天气、交通、酒店和景点信息。

## 功能特性

- 🤖 **智能Agent框架**：基于LangChain构建的智能对话系统
- 🌤️ **实时天气查询**：使用高德地图API获取目的地天气信息（支持4天预报）
- 🏨 **酒店价格估算**：智能估算酒店价格，支持经济型、舒适型、豪华型、民宿、青旅等多种类型
- 🚗 **交通路线规划**：支持飞机、高铁、火车、自驾、大巴等多种出行方式，提供路线、时间、费用估算
- 🎫 **景点门票查询**：使用天聚数行API或高德地图POI API查询景点信息和门票价格
- 🗺️ **行程规划**：根据目的地、天数、预算等自动生成详细行程，集成天气、酒店、交通、景点信息
- ❓ **景点问答**：回答关于景点的各种问题（开放时间、门票、最佳游览时间等）
- 🎯 **个性化推荐**：根据用户兴趣和旅行风格提供定制化推荐
- 💬 **对话记忆**：支持多轮对话，记住上下文信息
- 👤 **用户系统**：支持用户注册、登录，每个用户独立的会话
- 🌐 **Web界面**：现代化的聊天界面，支持实时对话和旅行信息表单

## 项目结构

```
LLM-Travel-Assistant/
├── src/                      # 源代码目录
│   ├── agent/               # Agent核心模块
│   │   ├── travel_agent.py  # 旅行助手Agent
│   │   └── tools.py         # Agent工具定义（天气、酒店、交通、景点）
│   ├── models/              # 数据模型
│   │   └── user.py         # 用户模型
│   ├── config.py            # 配置管理
│   └── main.py              # 命令行入口
├── templates/               # Web模板文件
│   ├── index.html          # 聊天界面模板
│   ├── login.html          # 登录页面
│   └── register.html       # 注册页面
├── data/                    # 数据目录
│   └── users.json          # 用户数据（Git忽略）
├── tests/                   # 测试文件
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

运行测试文件：

```bash
python tests/test_config.py      # 测试配置加载
python tests/test_import.py      # 测试模块导入
python scripts/test_api_connection.py  # 测试API连接
```

## 工具脚本

```bash
python scripts/example.py         # 运行使用示例
python scripts/test_api_connection.py  # 测试API连接
```

## 技术栈

- **LangChain**：Agent框架和工具链
- **OpenAI API / DeepSeek API**：LLM服务
- **高德地图API**：天气查询、路径规划
- **天聚数行API**：景点门票查询
- **Flask**：Web框架
- **Python 3.8+**：开发语言

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
- **自驾**：使用高德地图API获取路线、距离、时间、过路费
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
- [x] 交通路线规划
- [x] 景点门票查询
- [x] 酒店价格估算
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

## 注意事项

1. **API密钥安全**：请勿将包含真实API密钥的 `env` 文件提交到代码仓库
2. **用户数据**：用户数据存储在 `data/users.json`，已配置Git忽略
3. **API限制**：注意各API的调用频率限制，合理使用
4. **估算数据**：当API不可用时，系统会使用智能估算，实际价格可能有所不同
