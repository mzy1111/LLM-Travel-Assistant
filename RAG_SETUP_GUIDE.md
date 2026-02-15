# RAG系统安装和使用指南

## 问题说明

由于网络问题，pip无法自动安装pandas和chromadb。以下是几种解决方案：

## 解决方案1：使用国内镜像源（推荐）

### 方法1：使用阿里云镜像

```bash
pip install pandas chromadb tiktoken -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

### 方法2：使用清华镜像

```bash
pip install pandas chromadb tiktoken -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

### 方法3：使用豆瓣镜像

```bash
pip install pandas chromadb tiktoken -i https://pypi.douban.com/simple --trusted-host pypi.douban.com
```

## 解决方案2：手动下载whl文件安装

### 步骤1：下载whl文件

访问以下链接下载对应的whl文件：

- pandas: https://pypi.org/project/pandas/#files
- chromadb: https://pypi.org/project/chromadb/#files
- tiktoken: https://pypi.org/project/tiktoken/#files

选择与你的Python版本和操作系统匹配的whl文件。

### 步骤2：安装whl文件

```bash
pip install pandas-x.x.x-pxx-none-win_amd64.whl
pip install chromadb-x.x.x-pxx-none-any.whl
pip install tiktoken-x.x.x-pxx-none-any.whl
```

## 解决方案3：使用conda（如果有）

```bash
conda install pandas
pip install chromadb tiktoken
```

## 解决方案4：离线安装

如果有其他可以联网的机器：

1. 在联网机器上下载whl文件
2. 将whl文件复制到目标机器
3. 使用pip安装whl文件

## 验证安装

安装完成后，运行以下命令验证：

```bash
python -c "import pandas; import chromadb; import tiktoken; print('所有依赖已安装')"
```

## 初始化向量数据库

依赖安装完成后，运行：

```bash
python scripts/init_attraction_db.py
```

预期输出：
```
============================================================
初始化景点向量数据库
============================================================

1. 加载景点数据...
加载 上海 的景点数据：100 个景点
加载 北京 的景点数据：90 个景点
加载 天津 的景点数据：80 个景点
   加载了 3 个城市的数据：上海, 北京, 天津

2. 创建向量数据库...
切分后文档数量：xxx
向量数据库创建完成，文档数量：xxx

3. 测试搜索...

   测试查询：故宫 (城市：北京)
   找到 2 个结果
   1. 故宫博物院
   2. ...

============================================================
初始化完成！
============================================================
```

## 启动应用

```bash
python app.py
```

## 测试查询

在前端输入以下问题测试：

1. **搜索景点**：
   - "北京有什么历史景点？"
   - "推荐上海适合家庭游玩的景点"
   - "天津有什么好玩的？"

2. **查询景点详情**：
   - "故宫的开放时间是什么？"
   - "八达岭长城的门票价格"
   - "外滩的介绍"

3. **列出景点**：
   - "列出北京的所有景点"
   - "上海有哪些景点？"

## 常见问题

### Q1: 提示"OPENAI_API_KEY 未设置"

**A**: 确保在env文件中配置了OPENAI_API_KEY：

```bash
# 复制env.example为env
cp env.example env

# 编辑env文件，填入你的API密钥
OPENAI_API_KEY='your_actual_api_key_here'
```

### Q2: 提示"ModuleNotFoundError: No module named 'pandas'"

**A**: pandas未安装，请按照上述解决方案安装pandas。

### Q3: 向量数据库创建失败

**A**: 检查以下几点：
- 确保OPENAI_API_KEY已配置
- 确保网络可以访问OpenAI API
- 确保jingdian目录下有CSV文件

### Q4: 查询时没有结果

**A**: 可能的原因：
- 向量数据库未初始化，运行`python scripts/init_attraction_db.py`
- 查询的关键词与景点信息不匹配
- CSV文件格式不正确

## 系统架构

```
用户提问
    ↓
主协调Agent
    ↓
选择工具
    ↓
search_attraction_local / get_attraction_details_local / list_attractions_local
    ↓
向量检索
    ↓
返回相关景点信息
    ↓
LLM生成回答
    ↓
返回给用户
```

## 核心特性

### 1. 语义搜索
支持自然语言查询，能够理解语义相似性：
- "适合家庭游玩的景点" → 返回适合家庭的景点
- "历史景点" → 返回历史相关的景点
- "免费景点" → 返回免费的景点

### 2. 智能切分
使用RecursiveCharacterTextSplitter将长文本切分成小块：
- chunk_size: 500字符
- chunk_overlap: 50字符
- 分隔符：段落、行、句号、逗号、空格

### 3. 向量存储
使用ChromaDB存储向量：
- 持久化存储（chroma_db目录）
- 支持相似度搜索
- 自动加载已存在的数据库

### 4. 优先级策略
Agent优先使用本地数据：
1. 本地CSV数据（优先）
2. 高德API（备选）

## 数据格式

CSV文件应包含以下字段：
- 名字
- 链接
- 地址
- 介绍
- 开放时间
- 图片链接
- 评分
- 建议游玩时间
- 建议季节
- 门票
- 小贴士
- Page

## 扩展方法

要添加新的城市，只需：

1. 在jingdian目录下添加新的CSV文件（如`广州.csv`）
2. 运行初始化脚本：
   ```bash
   python scripts/init_attraction_db.py
   ```
3. 系统会自动加载新数据

## 技术栈

- **数据处理**：pandas
- **向量存储**：ChromaDB
- **文本切分**：LangChain RecursiveCharacterTextSplitter
- **向量化**：OpenAI Embeddings
- **Agent框架**：LangChain

## 注意事项

1. **首次运行**：必须先运行初始化脚本创建向量数据库
2. **数据更新**：如果CSV文件更新，需要重新运行初始化脚本
3. **API密钥**：虽然优先使用本地数据，但仍需配置OPENAI_API_KEY用于LLM生成
4. **网络问题**：如果pip安装失败，可以手动下载whl文件安装
