# 故障排查指南

## 连接错误问题

如果遇到"连接错误: 无法连接到AI服务"，请按以下步骤排查：

### 1. 检查API配置

运行测试脚本检查API连接：

```bash
python scripts/test_api_connection.py
```

### 2. 验证API密钥

**检查密钥格式：**
- 确保 `env` 文件中的 `OPENAI_API_KEY` 格式正确
- 不要有多余的空格或引号
- 示例：`OPENAI_API_KEY=sk-xxxxxxxxxxxxx`

**验证密钥有效性：**
- 登录您的API服务提供商（OpenAI/DeepSeek等）
- 检查密钥是否有效、未过期
- 确认密钥有足够的余额或配额

### 3. 检查API服务地址

**DeepSeek API：**
```env
OPENAI_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

**OpenAI API：**
```env
OPENAI_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo-preview
```

**其他兼容OpenAI API的服务：**
- 确保API地址格式正确
- 确认模型名称与服务提供商匹配

### 4. 网络连接问题

**检查网络连接：**
```bash
# 测试能否访问API服务器
ping api.deepseek.com  # DeepSeek
ping api.openai.com    # OpenAI
```

**代理设置：**
如果使用代理，需要配置环境变量：
```bash
# Windows PowerShell
$env:HTTP_PROXY="http://your-proxy:port"
$env:HTTPS_PROXY="http://your-proxy:port"

# Linux/Mac
export HTTP_PROXY="http://your-proxy:port"
export HTTPS_PROXY="http://your-proxy:port"
```

### 5. 防火墙和安全软件

- 检查防火墙是否阻止了Python访问网络
- 临时关闭安全软件测试
- 将Python添加到防火墙白名单

### 6. 常见错误及解决方案

#### 错误：`Connection error` 或 `Connection timeout`

**可能原因：**
- 网络连接不稳定
- API服务器暂时不可用
- 防火墙阻止连接

**解决方案：**
1. 检查网络连接
2. 稍后重试
3. 检查防火墙设置
4. 尝试使用VPN或代理

#### 错误：`API key is invalid` 或 `Authentication failed`

**可能原因：**
- API密钥错误
- API密钥已过期
- API密钥格式不正确

**解决方案：**
1. 重新生成API密钥
2. 检查 `env` 文件中的密钥格式
3. 确认密钥未过期

#### 错误：`Rate limit exceeded` 或 `Quota exceeded`

**可能原因：**
- API调用次数达到限制
- API余额不足

**解决方案：**
1. 检查API账户余额
2. 等待限制重置
3. 升级API套餐

#### 错误：`Model not found` 或 `Invalid model`

**可能原因：**
- 模型名称不正确
- 该服务不支持该模型

**解决方案：**
1. 检查模型名称是否正确
2. 查看服务提供商的可用模型列表
3. 使用正确的模型名称

### 7. 调试技巧

**启用详细日志：**
在 `app.py` 中，Agent初始化时设置 `verbose=True`：
```python
agents[session_id] = TravelAgent(verbose=True)
```

**查看完整错误信息：**
- 检查终端输出的错误堆栈
- 查看浏览器控制台的网络请求
- 检查Flask应用的日志输出

**手动测试API：**
```bash
# 使用curl测试（DeepSeek示例）
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# 使用Python测试
python scripts/test_api_connection.py
```

### 8. 获取帮助

如果以上方法都无法解决问题：

1. **检查项目文档：**
   - `README.md` - 项目概述和快速开始
   - `docs/RUN_GUIDE.md` - 运行指南
   - `docs/PROJECT_OVERVIEW.md` - 项目架构

2. **查看错误日志：**
   - 终端输出的完整错误信息
   - Flask调试模式下的详细日志

3. **验证环境：**
   ```bash
   # 检查Python版本
   python --version  # 需要3.8+
   
   # 检查依赖
   pip list | grep -E "openai|langchain|flask"
   
   # 重新安装依赖
   pip install -r requirements.txt --upgrade
   ```

### 9. DeepSeek API 特定问题

如果使用DeepSeek API，请注意：

1. **模型名称：**
   - 聊天模型：`deepseek-chat`
   - 嵌入模型：`deepseek-embed`

2. **API地址：**
   - 确保使用：`https://api.deepseek.com/v1`

3. **密钥格式：**
   - DeepSeek API密钥通常以 `sk-` 开头

4. **限制：**
   - 检查DeepSeek账户的调用限制
   - 确认账户状态正常

### 10. 快速修复清单

- [ ] 检查 `env` 文件中的 `OPENAI_API_KEY` 是否正确
- [ ] 运行 `python scripts/test_api_connection.py` 测试连接
- [ ] 检查网络连接是否正常
- [ ] 验证API密钥是否有效且有余额
- [ ] 确认API服务地址和模型名称正确
- [ ] 检查防火墙和安全软件设置
- [ ] 查看终端和浏览器的完整错误信息
- [ ] 尝试重新启动Flask应用

