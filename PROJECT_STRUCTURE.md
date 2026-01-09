# 项目目录结构

```
LLM-Travel-Assistant/
├── src/                      # 源代码目录
│   ├── agent/               # Agent核心模块
│   │   ├── travel_agent.py # 智能旅行助手Agent
│   │   └── tools.py         # Agent工具定义
│   ├── models/              # 数据模型
│   │   └── user.py         # 用户模型
│   ├── config.py            # 配置管理
│   └── main.py              # 命令行入口
│
├── templates/               # Web模板文件
│   ├── index.html          # 聊天界面模板
│   ├── login.html          # 登录页面
│   └── register.html       # 注册页面
│
├── data/                    # 数据目录
│   └── users.json          # 用户数据（Git忽略）
│
├── tests/                   # 测试文件
│   ├── test_config.py      # 配置测试
│   └── test_import.py      # 导入测试
│
├── scripts/                 # 工具脚本
│   ├── example.py          # 使用示例
│   └── test_api_connection.py # API连接测试
│
├── docs/                    # 文档目录
│   ├── PROJECT_OVERVIEW.md # 项目概述
│   ├── QUICK_START.md      # 快速开始指南
│   ├── README.md           # 文档说明
│   ├── RUN_GUIDE.md        # 运行指南
│   └── TROUBLESHOOTING.md  # 故障排除
│
├── app.py                   # Flask Web应用入口
├── config.yaml              # 配置文件
├── requirements.txt         # Python依赖
├── env.example              # 环境变量示例
├── README.md                # 项目说明
├── LICENSE                  # 许可证
└── .gitignore              # Git忽略文件
```

## 目录说明

### src/
核心源代码目录，包含所有业务逻辑。

- `agent/`: Agent核心模块，包含旅行助手和工具定义
- `models/`: 数据模型，包含用户模型
- `config.py`: 配置管理，加载环境变量和配置文件
- `main.py`: 命令行入口，用于命令行交互模式

### templates/
Web界面模板文件，使用Flask渲染。

- `index.html`: 主聊天界面，包含旅行信息表单和对话区域
- `login.html`: 用户登录页面
- `register.html`: 用户注册页面

### data/
数据存储目录，包括用户数据。

- `users.json`: 用户数据文件（Git忽略，不提交到仓库）

### tests/
测试文件目录，用于单元测试和集成测试。

### scripts/
工具脚本目录，包含辅助脚本和示例代码。

### docs/
文档目录，包含项目文档和使用指南。

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
python tests/test_config.py
python tests/test_import.py
```

### 工具脚本
```bash
python scripts/example.py
python scripts/test_api_connection.py
```
