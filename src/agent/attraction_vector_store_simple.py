"""
景点检索模块（简化版，不依赖ChromaDB）
"""
from typing import List, Optional, Tuple
from langchain.schema import Document
from src.agent.attraction_loader_simple import AttractionDataLoader


class AttractionVectorStore:
    """景点存储和检索（简化版，使用关键词搜索）"""

    def __init__(self, data_loader: AttractionDataLoader, persist_directory: str = "./chroma_db"):
        self.data_loader = data_loader
        self.persist_directory = persist_directory
        self.documents = []
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """初始化文档存储"""
        print("创建文档存储...")

        # 遍历所有城市的景点
        for city in self.data_loader.get_cities():
            attractions = self.data_loader.get_all_attractions(city)

            for attraction in attractions:
                # 创建文档
                content = f"""
景点名称：{attraction.get('名字', '')}
地址：{attraction.get('地址', '')}
介绍：{attraction.get('介绍', '')}
开放时间：{attraction.get('开放时间', '')}
评分：{attraction.get('评分', '')}
建议游玩时间：{attraction.get('建议游玩时间', '')}
建议季节：{attraction.get('建议季节', '')}
门票：{attraction.get('门票', '')}
小贴士：{attraction.get('小贴士', '')}
"""

                doc = Document(
                    page_content=content,
                    metadata={
                        "city": city,
                        "name": attraction.get('名字', ''),
                        "address": attraction.get('地址', ''),
                        "rating": attraction.get('评分', '')
                    }
                )
                self.documents.append(doc)

        print(f"文档存储创建完成，文档数量：{len(self.documents)}")

    def search(self, query: str, city: Optional[str] = None, k: int = 3) -> List[Document]:
        """搜索相关景点（使用关键词匹配）"""
        query_lower = query.lower()
        scored_docs = []

        for doc in self.documents:
            # 如果指定了城市，过滤结果
            if city and doc.metadata.get('city') != city:
                continue

            # 计算匹配分数
            score = self._calculate_score(doc, query_lower)

            if score > 0:
                scored_docs.append((doc, score))

        # 按分数排序，返回前k个
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        results = [doc for doc, score in scored_docs[:k]]

        return results

    def search_with_score(self, query: str, city: Optional[str] = None, k: int = 3) -> List[Tuple[Document, float]]:
        """搜索相关景点（带分数）"""
        query_lower = query.lower()
        scored_docs = []

        for doc in self.documents:
            # 如果指定了城市，过滤结果
            if city and doc.metadata.get('city') != city:
                continue

            # 计算匹配分数
            score = self._calculate_score(doc, query_lower)

            if score > 0:
                scored_docs.append((doc, score))

        # 按分数排序，返回前k个
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:k]

    def _calculate_score(self, doc: Document, query_lower: str) -> float:
        """计算文档与查询的匹配分数"""
        score = 0.0
        content_lower = doc.page_content.lower()

        # 完全匹配（最高分）
        if query_lower in content_lower:
            score += 10.0

        # 关键词匹配
        keywords = query_lower.split()
        for keyword in keywords:
            if len(keyword) < 2:  # 跳过单字
                continue
            if keyword in content_lower:
                score += 2.0

        # 元数据匹配
        metadata = doc.metadata
        name_lower = metadata.get('name', '').lower()
        address_lower = metadata.get('address', '').lower()

        if query_lower in name_lower:
            score += 5.0
        if query_lower in address_lower:
            score += 3.0

        # 语义匹配（基于常见关键词）
        semantic_keywords = {
            '历史': ['历史', '文化', '古迹', '博物馆', '宫殿', '寺庙', '古建筑'],
            '家庭': ['家庭', '亲子', '儿童', '小孩', '孩子', '适合家庭', '亲子游'],
            '免费': ['免费', '0元', '不需要门票'],
            '自然': ['自然', '公园', '山水', '风景', '景观'],
            '美食': ['美食', '小吃', '特色菜', '餐厅'],
        }

        for semantic_key, keywords_list in semantic_keywords.items():
            if semantic_key in query_lower:
                for kw in keywords_list:
                    if kw in content_lower or kw in name_lower:
                        score += 3.0
                        break

        return score
