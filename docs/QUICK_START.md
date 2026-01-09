# 快速开始指南

## 网络受限环境下的快速启动

如果您的网络无法访问 HuggingFace 或遇到连接超时问题，可以快速切换到简单模式：

### 方法1：修改配置文件（推荐）

编辑 `config.yaml`，将 `embedding.use_simple` 设置为 `true`：

```yaml
embedding:
  use_simple: true  # 直接使用简单文本匹配模式
```

然后运行：
```bash
python src/main.py
```

### 方法2：使用环境变量

设置环境变量强制使用简单模式：
```bash
# Windows PowerShell
$env:EMBEDDING_USE_SIMPLE="true"
python src/main.py
```

### 方法3：等待自动切换

程序会自动检测网络问题，如果检测到连接超时，会自动切换到简单模式（可能需要等待几秒）。

## 简单模式 vs 完整模式

- **简单模式**：基于词频的文本匹配，无需网络，启动快，但搜索精度较低
- **完整模式**：使用 sentence-transformers 模型，需要网络下载，启动慢，但搜索精度高

## 推荐方案

1. **网络正常时**：使用默认配置，让程序自动下载模型
2. **网络受限时**：设置 `use_simple: true`，快速启动
3. **有模型缓存时**：程序会自动使用本地缓存的模型

