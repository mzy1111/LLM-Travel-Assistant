# Agent测试套件说明

## 📋 测试概述

本测试套件专门针对多Agent架构进行深度测试，验证Agent的路由、Function Calling、记忆机制、性能和集成功能。

## 🎯 测试亮点

### 1. **多Agent架构测试**
- 验证主协调Agent（TravelAgent）如何路由到专门Agent
- 测试6个专门Agent的独立性和协作性
- 验证避免重复调用的优化机制

### 2. **Function Calling机制测试**
- 验证LLM如何选择正确的工具
- 测试参数提取的准确性
- 验证工具调用顺序的合理性

### 3. **记忆机制测试**
- 测试多轮对话的上下文保持
- 验证Agent记忆的隔离性
- 测试旅行信息的记忆和使用

### 4. **性能测试**
- 统计API调用次数
- 测量响应时间
- 验证性能优化效果（existing_*参数）

### 5. **集成测试**
- 完整流程端到端测试
- 多Agent协调测试
- 错误处理测试

## 📁 测试文件结构

```
tests/
├── fixtures/
│   ├── __init__.py
│   └── test_callback_handler.py    # 测试用CallbackHandler，追踪Agent调用
├── test_agent_routing.py            # Agent路由测试
├── test_function_calling.py         # Function Calling测试
├── test_agent_memory.py             # 记忆机制测试
├── test_agent_performance.py        # 性能测试
├── test_agent_integration.py        # 集成测试
└── test_agent_all.py                # 运行所有测试的主文件
```

## 🚀 运行测试

### 前置条件

1. **设置环境变量**
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   export AMAP_API_KEY=your_amap_api_key  # 可选，用于真实API测试
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

### 运行单个测试文件

```bash
# 测试Agent路由
python -m pytest tests/test_agent_routing.py -v

# 测试Function Calling
python -m pytest tests/test_function_calling.py -v

# 测试记忆机制
python -m pytest tests/test_agent_memory.py -v

# 测试性能
python -m pytest tests/test_agent_performance.py -v

# 测试集成
python -m pytest tests/test_agent_integration.py -v
```

### 运行所有Agent测试

```bash
# 使用pytest
python -m pytest tests/test_agent_*.py -v

# 或使用unittest
python tests/test_agent_all.py
```

## 📊 测试指标

### 路由准确率
- **目标**: > 95%
- **验证**: 主Agent能够正确识别用户意图并路由到对应的专门Agent

### 工具选择准确率
- **目标**: > 80%
- **验证**: LLM能够为不同查询选择正确的工具

### 避免重复调用
- **目标**: 每个Agent最多调用1次（理想情况）
- **验证**: 通过CallbackHandler统计每个Agent的调用次数

### 响应时间
- **单Agent调用**: < 30秒
- **多Agent协作**: < 60秒
- **平均响应时间**: < 20秒

### API调用优化
- **验证**: 使用existing_*参数时，减少重复API调用
- **方法**: 通过调用序列验证规划Agent是否在最后调用（复用已查询信息）

## 🔍 测试用CallbackHandler

`TestCallbackHandler`是一个自定义的CallbackHandler，用于追踪和记录：

- **工具调用**: 记录所有工具的执行情况
- **Agent动作**: 记录所有Agent的调用和参数
- **LLM调用**: 记录LLM的调用次数和耗时
- **执行序列**: 记录Agent和工具的调用顺序

### 使用示例

```python
from tests.fixtures.test_callback_handler import TestCallbackHandler
from src.agent.travel_agent import TravelAgent

# 创建Agent和CallbackHandler
agent = TravelAgent(verbose=False)
callback_handler = TestCallbackHandler()

# 执行查询
result = agent.query(
    "北京明天天气怎么样？",
    config={"callbacks": [callback_handler]}
)

# 获取测试摘要
summary = callback_handler.get_summary()
print(f"Agent调用次数: {summary['agent_calls']}")
print(f"调用序列: {summary['agent_call_sequence']}")
print(f"各Agent调用次数: {summary['agent_call_counts']}")
```

## 📈 测试报告示例

运行测试后，会输出详细的测试报告，包括：

```
✓ 路由测试通过: '北京明天天气怎么样？' -> 天气Agent (调用1次)
✓ 工具选择正确: '北京明天天气' -> query_weather_agent
✓ 多轮对话测试完成:
  - 总轮数: 4
  - 最终响应长度: 1234字符
  - 找到关键词: ['北京', '3', '5000']
✓ 多Agent性能测试:
  - 总耗时: 15.23秒
  - Agent调用次数: 4
  - 调用序列: query_transport_agent -> query_weather_agent -> query_hotel_agent -> query_planning_agent
```

## 🎓 面试亮点

这套测试方案在面试中可以体现以下技术能力：

1. **架构理解**: 深入理解多Agent架构的设计模式和协作机制
2. **测试思维**: 从架构层面设计测试，不仅关注功能，还关注性能和优化
3. **工程能力**: 使用CallbackHandler进行非侵入式测试，设计测试追踪机制
4. **问题解决**: 能够识别关键测试点（如避免重复调用），设计测试验证优化效果

## ⚠️ 注意事项

1. **API密钥**: 需要有效的OpenAI API密钥才能运行测试
2. **API费用**: 测试会调用真实的OpenAI API，会产生费用
3. **网络要求**: 需要能够访问OpenAI API
4. **测试时间**: 完整测试套件可能需要较长时间（10-30分钟）

## 🔧 故障排除

### 问题: 测试被跳过
**原因**: OPENAI_API_KEY未设置
**解决**: 设置环境变量 `export OPENAI_API_KEY=your_key`

### 问题: 测试超时
**原因**: 网络问题或API响应慢
**解决**: 检查网络连接，或增加超时时间

### 问题: Agent调用次数不符合预期
**原因**: LLM的决策可能因模型版本、温度等参数而变化
**解决**: 这是正常的，测试主要验证系统能够正常工作，而不是严格验证调用次数

## 📝 扩展测试

可以根据需要添加更多测试：

1. **边界条件测试**: 测试极端输入、无效参数等
2. **并发测试**: 测试多用户同时使用时的表现
3. **压力测试**: 测试系统在高负载下的表现
4. **回归测试**: 确保新功能不影响现有功能
