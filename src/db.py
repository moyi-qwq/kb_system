from elasticsearch import AsyncElasticsearch
from .config import settings
from .models import IndexMetadata

class ElasticsearchClient:
    _instance = None
    
    @classmethod
    async def get_client(cls) -> AsyncElasticsearch:
        if cls._instance is None:
            cls._instance = AsyncElasticsearch(
                hosts=[f"http://{settings.ES_HOST}:{settings.ES_PORT}"],
                basic_auth=(settings.ES_USER, settings.ES_PASSWORD) if settings.ES_USER and settings.ES_PASSWORD else None
            )
        return cls._instance
    
    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def create_index(cls, metadata: IndexMetadata, mappings: dict):
        es = await cls.get_client()
        await es.indices.create(
            index=metadata.name,
            mappings={
                "properties": {
                    **mappings,
                    "kb_type": {"type": "keyword"}
                }
            }
        )
        # 设置索引的元数据
        await es.index(
            index="kb_metadata",
            id=metadata.name,
            document=metadata.dict()
        )

    @classmethod
    async def get_index_type(cls, index_name: str) -> str:
        es = await cls.get_client()
        try:
            result = await es.get(index="kb_metadata", id=index_name)
            return result["_source"]["type"]
        except Exception:
            return None

    @classmethod
    async def list_indices_by_type(cls, kb_type: str) -> list:
        es = await cls.get_client()
        try:
            result = await es.search(
                index="kb_metadata",
                query={"term": {"type": kb_type}}
            )
            return [hit["_id"] for hit in result["hits"]["hits"]]
        except Exception:
            return []

    @classmethod
    async def delete_index(cls, index_name: str):
        es = await cls.get_client()
        await es.indices.delete(index=index_name)
        await es.delete(index="kb_metadata", id=index_name) 