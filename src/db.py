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
            # 创建索引
            await es.indices.create(
                index=metadata.name,
                mappings={"properties": mappings}
            )
            
            # 存储索引元数据
            await es.index(
                index="kb_metadata",
                id=metadata.name,
                document=metadata.dict()
            )
        except Exception as e:
            raise Exception(f"Failed to create index: {str(e)}")

    @classmethod
    async def get_index_type(cls, index_name: str) -> str:
        es = await cls.get_client()
        try:
            result = await es.get(index="kb_metadata", id=index_name)
            return result["_source"]["type"]
        except Exception:
            return None

    @classmethod
    async def list_indices_by_type(cls, index_type: str) -> list:
        es = await cls.get_client()
        try:
            result = await es.search(
                index="kb_metadata",
                query={"term": {"type": index_type}}
            )
            return [hit["_id"] for hit in result["hits"]["hits"]]
        except Exception:
            return []

    @classmethod
    async def delete_index(cls, index_name: str):
        es = await cls.get_client()
        try:
            # 删除索引
            await es.indices.delete(index=index_name)
            # 删除元数据
            await es.delete(index="kb_metadata", id=index_name)
        except Exception as e:
            raise Exception(f"Failed to delete index: {str(e)}") 