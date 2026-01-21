"""运行所有Agent测试的主测试文件"""
import os
import sys
import unittest
import warnings

# 抑制Pydantic弃用警告
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*dict.*method is deprecated.*')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入所有测试模块
import test_agent_routing
import test_function_calling
import test_agent_memory
import test_agent_performance
import test_agent_integration


def create_test_suite():
    """创建测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加各个测试模块
    suite.addTests(loader.loadTestsFromModule(test_agent_routing))
    suite.addTests(loader.loadTestsFromModule(test_function_calling))
    suite.addTests(loader.loadTestsFromModule(test_agent_memory))
    suite.addTests(loader.loadTestsFromModule(test_agent_performance))
    suite.addTests(loader.loadTestsFromModule(test_agent_integration))
    
    return suite


if __name__ == '__main__':
    # 检查环境变量
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠ 警告: OPENAI_API_KEY未设置，部分测试可能被跳过")
        print("请设置环境变量: export OPENAI_API_KEY=your_key")
        print()
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    suite = create_test_suite()
    result = runner.run(suite)
    
    # 输出测试摘要（更清晰的格式）
    print("\n" + "=" * 80)
    print("📊 测试摘要")
    print("=" * 80)
    print(f"总测试数: {result.testsRun}")
    print(f"✅ 成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失败: {len(result.failures)}")
    print(f"⚠️  错误: {len(result.errors)}")
    print(f"⏭️  跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            # 只显示最后一行错误信息
            last_line = traceback.split('\n')[-2] if '\n' in traceback else traceback[:100]
            print(f"  • {test}")
            print(f"    {last_line}")
    
    if result.errors:
        print("\n⚠️  错误的测试:")
        for test, traceback in result.errors:
            last_line = traceback.split('\n')[-2] if '\n' in traceback else traceback[:100]
            print(f"  • {test}")
            print(f"    {last_line}")
    
    print("=" * 80)
    
    # 返回退出码
    sys.exit(0 if result.wasSuccessful() else 1)
