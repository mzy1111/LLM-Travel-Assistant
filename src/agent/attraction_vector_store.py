"""
景点向量检索模块
"""
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from src.agent.attraction_loader import AttractionDataLoader
from src.config import config


class AttractionVectorStore:
    """景点向量存储和检索"""

    def __init__(self, data_loader: AttractionDataLoader, persist_directory: str = "./chroma_db"):
        self.data_loader = data_loader
        self.persist_directory = persist_directory
        self.vectorstore = None
        
        # 从配置获取API密钥
        import os
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY 未设置，请在 env 文件中配置API密钥")
        
        os.environ["OPENAI_API_KEY"] = config.openai_api_key
        
        # 构建参数字典
        embeddings_kwargs = {
            "openai_api_key": config.openai_api_key,
        }
        
        # 如果API base不是OpenAI默认值，需要设置
        if config.openai_api_base and "openai.com" not in config.openai_api_base:
            os.environ["OPENAI_API_BASE"] = config.openai_api_base
            embeddings_kwargs["openai_api_base"] = config.openai_api_base
        
        self.embeddings = OpenAIEmbeddings(**embeddings_kwargs)
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """初始化向量数据库"""
        # 尝试加载已存在的向量数据库
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="attractions"
            )
            print(f"加载已存在的向量数据库：{self.persist_directory}")
        except:
            # 如果不存在，创建新的
            print("创建新的向量数据库...")
            self._create_vectorstore()

    def _create_vectorstore(self):
        """创建向量数据库"""
        documents = []

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
                documents.append(doc)

        # 文本切分
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "，", " ", ""]
        )

        texts = text_splitter.split_documents(documents)
        print(f"切分后文档数量：{len(texts)}")

        # 创建向量数据库
        self.vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="attractions"
        )

        print(f"向量数据库创建完成，文档数量：{len(texts)}")

    def search(self, query: str, city: Optional[str] = None, k: int = 3) -> List[Document]:
        """搜索相关景点"""
        # 构建搜索查询
        search_query = query
        if city:
            search_query = f"{city} {query}"

        # 执行搜索
        results = self.vectorstore.similarity_search(
            query=search_query,
            k=k
        )

        # 如果指定了城市，过滤结果
        if city:
            results = [doc for doc in results if doc.metadata.get('city') == city]

        return results

    def search_with_score(self, query: str, city: Optional[str] = None, k: int = 3) -> List[tuple]:
        """搜索相关景点（带分数）"""
        search_query = query
        if city:
            search_query = f"{city} {query}"

        results = self.vectorstore.similarity_search_with_score(
            query=search_query,
            k=k
        )

        if city:
            results = [(doc, score) for doc, score in results if doc.metadata.get('city') == city]

        return results
