from elasticsearch import AsyncElasticsearch
from .config import ELASTICSEARCH_URL
from .models import IndexMetadata

class ElasticsearchClient:
    _instance = None
    
    @classmethod
    async def get_client(cls):
        if cls._instance is None:
            cls._instance = AsyncElasticsearch(
                ELASTICSEARCH_URL,
                verify_certs=False
            )
        return cls._instance
    
    @classmethod
    async def close(cls):
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def create_index(cls, metadata: IndexMetadata, mappings: dict):
        es = await cls.get_client()
        try:
            # 创建带前缀的索引名
            prefixed_index_name = f"{metadata.type}_{metadata.name}"
            
            # 创建索引
            await es.indices.create(
                index=prefixed_index_name,
                mappings={"properties": mappings}
            )
            
            return prefixed_index_name
        except Exception as e:
            raise Exception(f"Failed to create index: {str(e)}")

    @classmethod
    async def get_index_type(cls, index_name: str) -> str:
        # 从索引名中提取类型
        parts = index_name.split('_', 1)
        if len(parts) != 2:
            return None
        return parts[0]

    @classmethod
    async def list_indices_by_type(cls, index_type: str) -> list:
        es = await cls.get_client()
        try:
            # 获取所有索引
            indices = await es.indices.get_alias()
            # 过滤出指定类型的索引并移除前缀
            filtered_indices = []
            prefix = f"{index_type}_"
            for index_name in indices.keys():
                if index_name.startswith(prefix):
                    # 移除前缀返回给前端
                    filtered_indices.append(index_name[len(prefix):])
            return filtered_indices
        except Exception:
            return []

    @classmethod
    async def delete_index(cls, index_name: str):
        es = await cls.get_client()
        try:
            # 删除索引
            await es.indices.delete(index=index_name)
        except Exception as e:
            raise Exception(f"Failed to delete index: {str(e)}") 