from src.agent.attraction_loader_simple import AttractionDataLoader

# 创建加载器
loader = AttractionDataLoader(data_dir="jingdian")

# 测试1：精确匹配（应该失败，因为数据库中有英文部分）
print("测试1：精确匹配 '圣索菲亚大教堂'")
result1 = loader.get_attraction_by_name("哈尔滨", "圣索菲亚大教堂")
if result1:
    print(f"✅ 找到: {result1.get('名字')}")
else:
    print("❌ 未找到")
print()

# 测试2：完整名称匹配
print("测试2：完整名称 '圣索菲亚大教堂St. Sophia Cathedral'")
result2 = loader.get_attraction_by_name("哈尔滨", "圣索菲亚大教堂St. Sophia Cathedral")
if result2:
    print(f"✅ 找到: {result2.get('名字')}")
else:
    print("❌ 未找到")
print()

# 测试3：不指定城市（跨城市搜索）
print("测试3：不指定城市，搜索 '圣索菲亚大教堂'")
all_cities = loader.get_cities()
found = False
for city in all_cities:
    result3 = loader.get_attraction_by_name(city, "圣索菲亚大教堂")
    if result3:
        print(f"✅ 在 {city} 找到: {result3.get('名字')}")
        found = True
        break
if not found:
    print("❌ 未找到")
print()

# 测试4：显示景点详细信息
if result1:
    print("景点详细信息：")
    print(f"名字: {result1.get('名字')}")
    print(f"地址: {result1.get('地址')}")
    print(f"评分: {result1.get('评分')}")
    print(f"门票: {result1.get('门票')}")

