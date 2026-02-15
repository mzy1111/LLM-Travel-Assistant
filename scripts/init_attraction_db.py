"""
初始化景点向量数据库
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.attraction_loader import AttractionDataLoader
from src.agent.attraction_vector_store import AttractionVectorStore

def main():
    print("=" * 60)
    print("初始化景点向量数据库")
    print("=" * 60)

    # 创建数据加载器
    print("\n1. 加载景点数据...")
    loader = AttractionDataLoader(data_dir="jingdian")

    cities = loader.get_cities()
    print(f"   加载了 {len(cities)} 个城市的数据：{', '.join(cities)}")

    # 创建向量存储
    print("\n2. 创建向量数据库...")
    vector_store = AttractionVectorStore(loader, persist_directory="./chroma_db")

    print("\n3. 测试搜索...")
    test_queries = [
        ("故宫", "北京"),
        ("历史景点", "北京"),
        ("适合家庭游玩", "上海"),
    ]

    for query, city in test_queries:
        print(f"\n   测试查询：{query} (城市：{city})")
        results = vector_store.search(query=query, city=city, k=2)
        print(f"   找到 {len(results)} 个结果")
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.metadata.get('name', '未知')}")

    print("\n" + "=" * 60)
    print("初始化完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
