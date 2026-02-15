"""
景点数据加载模块
"""
import pandas as pd
import os
from typing import List, Dict, Optional
from pathlib import Path


class AttractionDataLoader:
    """景点数据加载器"""

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
                df = pd.read_csv(csv_file)
                self.attractions[city_name] = df
                print(f"加载 {city_name} 的景点数据：{len(df)} 个景点")
            except Exception as e:
                print(f"加载 {csv_file} 失败：{e}")

    def get_cities(self) -> List[str]:
        """获取所有城市列表"""
        return list(self.attractions.keys())

    def get_attractions(self, city: str) -> pd.DataFrame:
        """获取指定城市的所有景点"""
        return self.attractions.get(city, pd.DataFrame())

    def search_attraction(self, city: str, keyword: str) -> List[Dict]:
        """搜索指定城市的景点"""
        if city not in self.attractions:
            return []

        df = self.attractions[city]

        # 在名字和介绍中搜索关键词
        mask = df['名字'].str.contains(keyword, case=False, na=False) | \
               df['介绍'].str.contains(keyword, case=False, na=False)

        results = df[mask].to_dict('records')
        return results

    def get_attraction_by_name(self, city: str, name: str) -> Optional[Dict]:
        """根据名称获取景点"""
        if city not in self.attractions:
            return None

        df = self.attractions[city]
        result = df[df['名字'] == name]

        if len(result) > 0:
            return result.iloc[0].to_dict()
        return None

    def get_all_attractions(self, city: str) -> List[Dict]:
        """获取指定城市的所有景点（返回字典列表）"""
        if city not in self.attractions:
            return []

        return self.attractions[city].to_dict('records')
