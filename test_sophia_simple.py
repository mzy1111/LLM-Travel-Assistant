from src.agent.attraction_loader_simple import AttractionDataLoader

# 创建加载器
loader = AttractionDataLoader(data_dir="jingdian")

# 测试：用户输入"圣索菲亚大教堂"
print("测试：查询 '圣索菲亚大教堂'")
result = loader.get_attraction_by_name("哈尔滨", "圣索菲亚大教堂")

if result:
    print("成功找到景点！")
    print("名字:", result.get('名字'))
    print("地址:", result.get('地址'))
    print("评分:", result.get('评分'))
    print("门票:", result.get('门票'))
else:
    print("未找到景点")

