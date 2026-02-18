import csv

# 读取哈尔滨景点数据
with open('jingdian/哈尔滨.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
print(f'总共 {len(rows)} 个景点')
print()

# 搜索圣索菲亚相关景点
sophia_attractions = [r for r in rows if '圣索菲亚' in r.get('名字', '')]
print(f'找到圣索菲亚相关景点: {len(sophia_attractions)}')
for s in sophia_attractions:
    print(f"  - {s.get('名字')}")
print()

# 搜索包含"教堂"的景点
church_attractions = [r for r in rows if '教堂' in r.get('名字', '')]
print(f'找到教堂相关景点: {len(church_attractions)}')
for c in church_attractions[:10]:
    print(f"  - {c.get('名字')}")

