# 如何运行单个测试方法

## 方法1: 使用unittest命令行（推荐）

### 运行单个测试方法

```bash
# 运行 TestAgentRouting 类的 test_weather_routing 方法
python -m unittest tests.test_agent_routing.TestAgentRouting.test_weather_routing

# 运行 TestAgentRouting 类的 test_transport_routing 方法
python -m unittest tests.test_agent_routing.TestAgentRouting.test_transport_routing

# 运行 TestAgentRouting 类的 test_hotel_routing 方法
python -m unittest tests.test_agent_routing.TestAgentRouting.test_hotel_routing

# 运行 TestAgentRouting 类的 test_attraction_routing 方法
python -m unittest tests.test_agent_routing.TestAgentRouting.test_attraction_routing

# 运行 TestAgentRouting 类的 test_planning_routing 方法
python -m unittest tests.test_agent_routing.TestAgentRouting.test_planning_routing

# 运行 TestAgentRouting 类的 test_multi_agent_routing 方法
python -m unittest tests.test_agent_routing.TestAgentRouting.test_multi_agent_routing
```

### 运行整个测试类

```bash
# 运行 TestAgentRouting 类的所有测试
python -m unittest tests.test_agent_routing.TestAgentRouting

# 运行整个测试模块
python -m unittest tests.test_agent_routing
```

## 方法2: 使用pytest（如果已安装）

```bash
# 运行单个测试方法
pytest tests/test_agent_routing.py::TestAgentRouting::test_weather_routing -v

# 运行整个测试类
pytest tests/test_agent_routing.py::TestAgentRouting -v

# 运行整个测试文件
pytest tests/test_agent_routing.py -v
```

## 方法3: 在Python代码中直接运行

创建一个临时脚本 `run_single_test.py`:

```python
import os
import sys
import unittest
import warnings

# 抑制Pydantic警告
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*dict.*method is deprecated.*')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_agent_routing import TestAgentRouting

# 创建测试套件
suite = unittest.TestSuite()
suite.addTest(TestAgentRouting('test_weather_routing'))  # 修改这里来运行不同的测试方法

# 运行测试
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# 输出结果
print(f"\n测试完成: {result.testsRun} 个测试")
print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
print(f"失败: {len(result.failures)}")
print(f"错误: {len(result.errors)}")
```

然后运行:
```bash
python run_single_test.py
```

## 方法4: 在VS Code中运行

1. 打开测试文件 `tests/test_agent_routing.py`
2. 找到要运行的测试方法（如 `test_weather_routing`）
3. 点击方法名上方的 "Run Test" 按钮（或右键选择 "Run Test"）

## 可用的测试方法

### TestAgentRouting 类
- `test_weather_routing` - 测试天气查询路由
- `test_transport_routing` - 测试交通路线路由
- `test_hotel_routing` - 测试酒店查询路由
- `test_attraction_routing` - 测试景点查询路由
- `test_planning_routing` - 测试行程规划路由
- `test_multi_agent_routing` - 测试多Agent协作路由

### TestFunctionCalling 类
- `test_tool_selection_accuracy` - 测试工具选择准确性
- `test_parameter_extraction` - 测试参数提取
- `test_tool_call_sequence` - 测试工具调用顺序
- `test_no_duplicate_calls` - 测试避免重复调用

### TestAgentMemory 类
- `test_multi_turn_conversation` - 测试多轮对话
- `test_context_persistence` - 测试上下文持久性
- `test_agent_memory_isolation` - 测试Agent记忆隔离
- `test_travel_info_memory` - 测试旅行信息记忆

### TestAgentPerformance 类
- `test_single_agent_performance` - 测试单Agent性能
- `test_multi_agent_performance` - 测试多Agent性能
- `test_no_duplicate_agent_calls` - 测试避免重复调用
- `test_api_call_optimization` - 测试API调用优化
- `test_response_time_distribution` - 测试响应时间分布

### TestAgentIntegration 类
- `test_complete_travel_planning_flow` - 测试完整旅行规划流程
- `test_weather_to_planning_flow` - 测试从天气到规划的流程
- `test_multi_agent_coordination` - 测试多Agent协调
- `test_error_handling` - 测试错误处理
- `test_streaming_response` - 测试流式响应

## 注意事项

1. **环境变量**: 确保设置了 `OPENAI_API_KEY` 环境变量
2. **警告抑制**: 所有测试文件已配置抑制Pydantic弃用警告，日志会更清晰
3. **测试时间**: 单个测试可能需要几秒到几十秒，取决于API响应速度
4. **费用**: 测试会调用真实的OpenAI API，会产生费用
