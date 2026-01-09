# 项目运行指南

## 快速开始

### 1. 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 2. 安装依赖

```bash
# 进入项目目录
cd LLM-Travel-Assistant

# 安装所有依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

**方式1：复制示例文件并编辑**

```bash
# Windows PowerShell
Copy-Item env.example .env

# 或直接复制 env.example 为 env
Copy-Item env.example env
```

**方式2：直接编辑 env 文件**

编辑 `env` 文件，填入您的配置：

```env
# OpenAI API配置
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 如果使用 DeepSeek，修改为：
# OPENAI_API_BASE=https://api.deepseek.com/v1
# LLM_MODEL=deepseek-chat
```

### 4. 运行项目

#### 方式1：Web界面（推荐）

```bash
python app.py
```

然后在浏览器中访问：`http://127.0.0.1:5000`

#### 方式2：命令行界面

```bash
python src/main.py
```

## 详细步骤

### 步骤1：检查Python版本

```bash
python --version
# 应该显示 Python 3.8 或更高版本
```

### 步骤2：创建虚拟环境（可选但推荐）

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Windows CMD:
.venv\Scripts\activate.bat

# Linux/Mac:
source .venv/bin/activate
```

### 步骤3：安装依赖

```bash
pip install -r requirements.txt
```

如果遇到网络问题，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤4：配置API密钥

**重要：必须配置API密钥才能运行！**

1. 打开 `env` 文件（如果不存在，复制 `env.example`）
2. 设置 `OPENAI_API_KEY` 为您的API密钥

```env
OPENAI_API_KEY=sk-your-api-key-here
```

**支持的API提供商：**
- OpenAI: `https://api.openai.com/v1`
- DeepSeek: `https://api.deepseek.com/v1`
- 其他兼容OpenAI API的服务

### 步骤5：准备知识库（可选）

项目已包含示例知识库文档在 `data/knowledge_base/` 目录：
- `beijing_attractions.txt` - 北京景点信息
- `travel_tips.txt` - 旅行建议

您可以添加更多文档（txt、pdf、csv、json格式）来扩展知识库。

### 步骤6：运行项目

#### Web界面运行

```bash
python app.py
```

**输出示例：**
```
正在初始化知识库...
找到 2 个文档，正在添加到向量数据库...
使用本地嵌入模型 (sentence-transformers)...
知识库初始化完成！

============================================================
智能旅行助手 Web 界面
============================================================
访问地址: http://127.0.0.1:5000
按 Ctrl+C 停止服务器
============================================================

 * Running on http://127.0.0.1:5000
```

**访问方式：**
- 本地访问：`http://127.0.0.1:5000`
- 局域网访问：`http://192.168.x.x:5000`（显示在启动信息中）

#### 命令行界面运行

```bash
python src/main.py
```

**使用方式：**
```
您: 帮我规划一个3天的北京行程，预算5000元
助手: [生成行程规划...]

您: 故宫的开放时间是什么？
助手: [回答开放时间...]
```

## 常见问题

### Q1: 提示 "未设置 OPENAI_API_KEY"

**解决方法：**
1. 检查 `env` 或 `.env` 文件是否存在
2. 确认文件中包含 `OPENAI_API_KEY=your_key`
3. 重启程序

### Q2: 网络连接问题，无法下载嵌入模型

**解决方法：**

**方案1：使用简单模式（推荐）**

编辑 `config.yaml`：
```yaml
embedding:
  use_simple: true  # 设置为 true
```

**方案2：手动下载模型**

```bash
python scripts/download_model.py
```

**方案3：配置代理**

如果使用代理，设置环境变量：
```bash
# Windows PowerShell
$env:HTTP_PROXY="http://your-proxy:port"
$env:HTTPS_PROXY="http://your-proxy:port"
```

### Q3: 端口5000已被占用

**解决方法：**

修改 `app.py` 最后一行：
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 改为其他端口
```

### Q4: 导入模块错误

**解决方法：**

确保在项目根目录运行：
```bash
# 检查当前目录
pwd  # Linux/Mac
cd   # Windows

# 应该在 LLM-Travel-Assistant 目录
```

### Q5: ChromaDB 相关错误

**解决方法：**

删除旧的向量数据库，重新初始化：
```bash
# 删除数据目录
rm -rf data/chroma_db  # Linux/Mac
Remove-Item -Recurse -Force data\chroma_db  # Windows PowerShell

# 重新运行程序，会自动重建
```

## 验证安装

运行测试脚本验证安装：

```bash
# 测试配置加载
python tests/test_config.py

# 测试模块导入
python tests/test_import.py

# 测试向量存储
python tests/test_vector_store.py
```

## 开发模式

### 启用调试模式

`app.py` 默认已启用调试模式：
```python
app.run(debug=True, ...)
```

### 查看日志

程序运行时会输出详细日志，包括：
- 知识库初始化状态
- Agent执行过程
- API调用信息

## 生产环境部署

### 使用 Gunicorn（Linux/Mac）

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Waitress（Windows）

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### 环境变量配置

生产环境建议：
1. 使用 `.env` 文件（不要提交到Git）
2. 设置强密码的 `app.secret_key`
3. 关闭调试模式：`app.run(debug=False)`

## 下一步

- 查看 [项目概述](PROJECT_OVERVIEW.md) 了解架构
- 查看 [快速开始](QUICK_START.md) 了解网络受限环境下的使用
- 查看 [项目结构](PROJECT_STRUCTURE.md) 了解目录组织

