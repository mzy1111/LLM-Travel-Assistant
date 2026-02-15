"""景点数据RAG加载和查询模块"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from src.config import config


class AttractionRAG:
    """景点数据RAG管理器"""
    
    def __init__(self, data_dir: str = "jingdian", persist_dir: str = "data/vector_store/attractions"):
        """
        初始化RAG管理器
        
        Args:
            data_dir: 景点CSV文件目录（默认为根目录的jingdian文件夹，包含全国352个城市数据）
            persist_dir: 向量数据库持久化目录
        """
        self.data_dir = Path(data_dir)
        self.persist_dir = Path(persist_dir)
        self.vectorstore = None
        self.embeddings = None
        
        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化embeddings
        self._init_embeddings()
        
        # 加载或创建向量数据库
        self._load_or_create_vectorstore()
    
    def _init_embeddings(self):
        """初始化Embedding模型"""
        # 优先使用本地模型（更稳定，不依赖API）
        from langchain_community.embeddings import HuggingFaceEmbeddings
        
        # 尝试多个模型，按优先级排序
        models_to_try = [
            ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "多语言模型(支持中文)"),
            ("shibing624/text2vec-base-chinese", "中文专用模型"),
        ]
        
        for model_name, model_desc in models_to_try:
            try:
                print(f"[INFO] 尝试加载{model_desc}: {model_name}")
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                print(f"[OK] 成功加载{model_desc}")
                return
            except Exception as e:
                print(f"[WARN] {model_desc}加载失败: {e}")
                continue
        
        # 所有本地模型都失败，抛出错误
        raise RuntimeError(
            "无法加载任何本地Embedding模型。请确保:\n"
            "1. 已安装sentence-transformers: pip install sentence-transformers\n"
            "2. 网络连接正常，可以访问HuggingFace\n"
            "3. 或手动下载模型到本地缓存目录"
        )
    
    def _load_or_create_vectorstore(self):
        """加载或创建向量数据库"""
        # 检查是否已有持久化的向量数据库
        if (self.persist_dir / "chroma.sqlite3").exists():
            print("[INFO] 加载已有的向量数据库...")
            try:
                self.vectorstore = Chroma(
                    persist_directory=str(self.persist_dir),
                    embedding_function=self.embeddings
                )
                count = self.vectorstore._collection.count()
                print(f"[OK] 向量数据库加载完成，包含 {count} 条记录")
            except Exception as e:
                print(f"[WARN] 加载向量数据库失败: {e}，将创建新的数据库")
                self.vectorstore = Chroma(
                    persist_directory=str(self.persist_dir),
                    embedding_function=self.embeddings
                )
                self._load_all_attractions()
        else:
            print("[INFO] 创建新的向量数据库...")
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_dir),
                embedding_function=self.embeddings
            )
            # 加载所有景点数据
            self._load_all_attractions()
    
    def _load_all_attractions(self):
        """加载所有城市的景点数据到向量数据库"""
        csv_files = list(self.data_dir.glob("*.csv"))
        
        if not csv_files:
            print("[WARN] 未找到任何景点CSV文件")
            print(f"   请在 {self.data_dir} 目录下添加城市景点CSV文件")
            return
        
        print(f"[INFO] 开始加载 {len(csv_files)} 个城市的景点数据...")
        
        all_documents = []
        for csv_file in csv_files:
            city_name = csv_file.stem  # 文件名即城市名
            try:
                documents = self._load_city_attractions(csv_file, city_name)
                all_documents.extend(documents)
                print(f"  [OK] {city_name}: {len(documents)} 个景点")
            except Exception as e:
                print(f"  [ERROR] {city_name}: 加载失败 - {e}")
        
        if all_documents:
            # 批量添加到向量数据库
            print(f"[INFO] 正在将 {len(all_documents)} 个景点添加到向量数据库...")
            batch_size = 100
            for i in range(0, len(all_documents), batch_size):
                batch = all_documents[i:i+batch_size]
                self.vectorstore.add_documents(batch)
                print(f"   进度: {min(i+batch_size, len(all_documents))}/{len(all_documents)}")
            print(f"[OK] 总共加载 {len(all_documents)} 个景点到向量数据库")
        else:
            print("[WARN] 没有成功加载任何景点数据")
    
    def _load_city_attractions(self, csv_file: Path, city_name: str) -> List[Document]:
        """
        加载单个城市的景点数据
        
        Args:
            csv_file: CSV文件路径
            city_name: 城市名称
            
        Returns:
            Document列表
        """
        documents = []
        
        # 读取CSV文件
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_file, encoding='gbk')
        
        # 为每个景点创建一个Document
        for idx, row in df.iterrows():
            # 构建景点的文本描述（用于embedding）
            content = self._format_attraction_content(row, city_name)
            
            # 创建Document，包含元数据
            doc = Document(
                page_content=content,
                metadata={
                    "city": city_name,
                    "name": str(row.get("名字", "")),
                    "address": str(row.get("地址", "")),
                    "type": str(row.get("介绍", ""))[:50] if pd.notna(row.get("介绍")) else "",  # 取简介前50字作为类型
                    "rating": str(row.get("评分", "")),
                    "ticket": str(row.get("门票", "")),
                    "hours": str(row.get("开放时间", "")),
                    "tags": str(row.get("建议季节", "")),
                    "source": str(csv_file)
                }
            )
            documents.append(doc)
        
        return documents
    
    def _format_attraction_content(self, row: pd.Series, city_name: str) -> str:
        """
        格式化景点内容为文本描述
        
        Args:
            row: DataFrame行数据
            city_name: 城市名称
            
        Returns:
            格式化的文本描述
        """
        parts = []
        
        parts.append(f"城市：{city_name}")
        
        # 使用CSV文件中的实际列名
        if pd.notna(row.get('名字')):
            parts.append(f"景点名称：{row.get('名字')}")
        
        if pd.notna(row.get('介绍')):
            parts.append(f"简介：{row.get('介绍')}")
        
        if pd.notna(row.get('评分')):
            parts.append(f"评分：{row.get('评分')}")
        
        if pd.notna(row.get('门票')):
            parts.append(f"门票：{row.get('门票')}")
        
        if pd.notna(row.get('开放时间')):
            parts.append(f"开放时间：{row.get('开放时间')}")
        
        if pd.notna(row.get('地址')):
            parts.append(f"地址：{row.get('地址')}")
        
        if pd.notna(row.get('建议游玩时间')):
            parts.append(f"建议游玩时间：{row.get('建议游玩时间')}")
        
        if pd.notna(row.get('建议季节')):
            parts.append(f"建议季节：{row.get('建议季节')}")
        
        return "\n".join(parts)
    
    def search_attractions(self, query: str, city: Optional[str] = None, k: int = 5) -> List[Dict]:
        """
        搜索景点
        
        Args:
            query: 查询文本，如"历史文化景点"、"适合亲子游的地方"
            city: 可选，限定城市
            k: 返回结果数量
            
        Returns:
            景点信息列表
        """
        if not self.vectorstore:
            return []
        
        # 构建查询文本
        search_query = query
        if city:
            search_query = f"{city} {query}"
        
        try:
            # 执行相似度搜索
            if city:
                # 如果指定了城市，使用元数据过滤
                results = self.vectorstore.similarity_search(
                    search_query,
                    k=k,
                    filter={"city": city}
                )
            else:
                results = self.vectorstore.similarity_search(search_query, k=k)
        except Exception as e:
            print(f"[WARN] 搜索失败: {e}")
            return []
        
        # 格式化结果
        attractions = []
        for doc in results:
            attraction = {
                "city": doc.metadata.get("city", ""),
                "name": doc.metadata.get("name", ""),
                "address": doc.metadata.get("address", ""),
                "area": doc.metadata.get("area", ""),
                "type": doc.metadata.get("type", ""),
                "rating": doc.metadata.get("rating", ""),
                "price": doc.metadata.get("price", ""),
                "hours": doc.metadata.get("hours", ""),
                "ticket": doc.metadata.get("ticket", ""),
                "tags": doc.metadata.get("tags", ""),
                "content": doc.page_content
            }
            attractions.append(attraction)
        
        return attractions
    
    def get_city_attractions(self, city: str, limit: int = 20) -> List[Dict]:
        """
        获取指定城市的所有景点
        
        Args:
            city: 城市名称
            limit: 返回数量限制
            
        Returns:
            景点信息列表
        """
        return self.search_attractions("景点", city=city, k=limit)
    
    def add_city_attractions(self, csv_file: str):
        """
        添加新城市的景点数据
        
        Args:
            csv_file: CSV文件路径
        """
        csv_path = Path(csv_file)
        if not csv_path.exists():
            raise FileNotFoundError(f"文件不存在: {csv_file}")
        
        city_name = csv_path.stem
        documents = self._load_city_attractions(csv_path, city_name)
        
        if documents:
            self.vectorstore.add_documents(documents)
            print(f"[OK] 成功添加 {city_name} 的 {len(documents)} 个景点")
        else:
            print(f"[WARN] {city_name} 没有有效的景点数据")
    
    def rebuild_index(self):
        """重建向量索引（当数据更新时使用）"""
        print("[INFO] 重建向量索引...")
        
        # 清空现有数据
        if self.vectorstore:
            try:
                self.vectorstore._collection.delete()
            except:
                pass
        
        # 重新创建向量数据库
        self.vectorstore = Chroma(
            persist_directory=str(self.persist_dir),
            embedding_function=self.embeddings
        )
        
        # 重新加载所有数据
        self._load_all_attractions()
        print("[OK] 向量索引重建完成")


# 全局单例
_attraction_rag = None

def get_attraction_rag() -> AttractionRAG:
    """获取景点RAG管理器单例"""
    global _attraction_rag
    if _attraction_rag is None:
        _attraction_rag = AttractionRAG()
    return _attraction_rag

