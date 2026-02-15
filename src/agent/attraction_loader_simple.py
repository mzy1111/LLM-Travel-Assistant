"""
景点数据加载模块（简化版，不依赖pandas）
"""
import csv
import os
from typing import List, Dict, Optional
from pathlib import Path


class AttractionDataLoader:
    """景点数据加载器（简化版）"""

    def __init__(self, data_dir: str = "jingdian"):
        self.data_dir = Path(data_dir)
        self.attractions = {}
        self._load_data()

    def _load_data(self):
        """加载所有CSV文件"""
        if not self.data_dir.exists():
            print(f"警告：数据目录 {self.data_dir} 不存在")
            return

        # 遍历所有CSV文件
        for csv_file in self.data_dir.glob("*.csv"):
            city_name = csv_file.stem
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    attractions = list(reader)
                    self.attractions[city_name] = attractions
                    print(f"加载 {city_name} 的景点数据：{len(attractions)} 个景点")
            except Exception as e:
                print(f"加载 {csv_file} 失败：{e}")

    def get_cities(self) -> List[str]:
        """获取所有城市列表"""
        return list(self.attractions.keys())

    def get_attractions(self, city: str) -> List[Dict]:
        """获取指定城市的所有景点"""
        return self.attractions.get(city, [])

    def search_attraction(self, city: str, keyword: str) -> List[Dict]:
        """搜索指定城市的景点"""
        if city not in self.attractions:
            return []

        attractions = self.attractions[city]
        results = []

        for attraction in attractions:
            name = attraction.get('名字', '')
            intro = attraction.get('介绍', '')
            if keyword.lower() in name.lower() or keyword.lower() in intro.lower():
                results.append(attraction)

        return results

    def get_attraction_by_name(self, city: str, name: str) -> Optional[Dict]:
        """根据名称获取景点"""
        if city not in self.attractions:
            return None

        attractions = self.attractions[city]
        for attraction in attractions:
            if attraction.get('名字') == name:
                return attraction
        return None

    def get_all_attractions(self, city: str) -> List[Dict]:
        """获取指定城市的所有景点（返回字典列表）"""
        return self.attractions.get(city, [])
