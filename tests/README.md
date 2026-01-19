# Agent单元测试说明

## 测试文件结构

- `test_agent_tools.py` - 测试工具函数（使用mock，不需要真实API密钥）
- `test_agent_api_connection.py` - 测试与第三方API的实际连接（需要配置API密钥）
- `test_specialized_agents.py` - 测试专门Agent的创建和初始化
- `run_all_tests.py` - 运行所有测试的脚本

## 运行测试

### 1. 运行所有测试（推荐）

```bash
python tests/run_all_tests.py
```

### 2. 运行特定测试文件

```bash
# 测试工具函数（不需要API密钥）
python -m pytest tests/test_agent_tools.py -v

# 测试API连接（需要API密钥）
python -m pytest tests/test_agent_api_connection.py -v

# 测试专门Agent
python -m pytest tests/test_specialized_agents.py -v
```

### 3. 使用unittest运行

```bash
# 运行所有测试
python -m unittest discover tests -v

# 运行特定测试类
python -m unittest tests.test_agent_tools.TestWeatherTool -v
```

## 测试内容

### test_agent_tools.py
- ✅ 天气工具API调用（mock）
- ✅ 交通工具API调用（mock）
- ✅ 酒店工具基本功能
- ✅ 景点工具API调用（mock）
- ✅ 行程规划工具集成测试
- ✅ 工具导入测试

### test_agent_api_connection.py
- ✅ 天气API实际连接测试（需要AMAP_API_KEY）
- ✅ 交通API实际连接测试（需要AMAP_API_KEY）
- ✅ 酒店工具基本功能测试
- ✅ 景点API实际连接测试（需要AMAP_API_KEY，使用高德地图POI API）
- ✅ 错误处理测试

### test_specialized_agents.py
- ✅ WeatherAgent创建测试
- ✅ TransportAgent创建测试
- ✅ HotelAgent创建测试
- ✅ AttractionAgent创建测试
- ✅ PlanningAgent创建测试
- ✅ RecommendationAgent创建测试

## 配置API密钥

要运行实际API连接测试，需要在`env`文件中配置以下密钥：

```bash
# 高德地图API（用于天气、交通和景点查询）
AMAP_API_KEY='your_amap_api_key_here'
```

如果没有配置API密钥，相关测试会被自动跳过。

## 测试输出示例

```
============================================================
Agent工具第三方API连接测试
============================================================

注意：此测试需要配置相应的API密钥
如果API密钥未配置，相关测试将被跳过

test_weather_api_real_connection ... ✓ 天气API测试成功: 北京在2026-01-17的天气：晴，温度15-25°C...
ok
test_transport_api_real_connection ... ✓ 交通API测试成功: 北京到上海的自驾路线：距离1200.0公里...
ok
test_hotel_tool_basic ... ✓ 酒店工具测试成功: 北京在2026-01-17至2026-01-18期间的酒店价格估算...
ok

----------------------------------------------------------------------
Ran 3 tests in 2.345s

OK
```

## 注意事项

1. **Mock测试**：`test_agent_tools.py`使用mock，不需要真实API密钥，适合CI/CD环境
2. **真实API测试**：`test_agent_api_connection.py`需要真实API密钥，会实际调用第三方API
3. **网络依赖**：真实API测试需要网络连接
4. **API配额**：真实API测试会消耗API调用配额，请谨慎使用

