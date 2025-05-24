from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from ..models import HistoryItem, IndexMetadata
from ..db import ElasticsearchClient

router = APIRouter()

@router.get("/list")
async def get_history_list():
    es = await ElasticsearchClient.get_client()
    try:
        indices = await ElasticsearchClient.list_indices_by_type("history")
        return {"indices": indices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{index_name}/items")
async def get_history_items(index_name: str):
    es = await ElasticsearchClient.get_client()
    try:
        # 添加前缀
        prefixed_index_name = f"history_{index_name}"
        result = await es.search(
            index=prefixed_index_name,
            query={"match_all": {}}
        )
        items = [{"uid": hit["_id"], "name": hit["_source"]["name"]} 
                for hit in result["hits"]["hits"]]
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{index_name}/items/{uid}")
async def get_history_item(index_name: str, uid: str):
    es = await ElasticsearchClient.get_client()
    try:
        # 添加前缀
        prefixed_index_name = f"history_{index_name}"
        result = await es.get(index=prefixed_index_name, id=uid)
        return result["_source"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{index_name}")
async def create_history_index(index_name: str):
    es = await ElasticsearchClient.get_client()
    try:
        metadata = IndexMetadata(name=index_name, type="history")
        mappings = {
            "name": {"type": "keyword"},
            "input": {"type": "text"},
            "output": {"type": "text"},
            "details": {"type": "text"}
        }
        prefixed_index_name = await ElasticsearchClient.create_index(metadata, mappings)
        return {"message": f"Index {index_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{index_name}/items")
async def create_history_item(index_name: str, item: HistoryItem):
    es = await ElasticsearchClient.get_client()
    try:
        # 添加前缀
        prefixed_index_name = f"history_{index_name}"
        uid = str(uuid.uuid4())
        await es.index(
            index=prefixed_index_name,
            id=uid,
            document=item.model_dump()
        )
        return {"message": "Item created successfully", "uid": uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{index_name}")
async def delete_history_index(index_name: str):
    es = await ElasticsearchClient.get_client()
    try:
        # 添加前缀
        prefixed_index_name = f"history_{index_name}"
        await ElasticsearchClient.delete_index(prefixed_index_name)
        return {"message": f"Index {index_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{index_name}/items/{uid}")
async def delete_history_item(index_name: str, uid: str):
    es = await ElasticsearchClient.get_client()
    try:
        # 添加前缀
        prefixed_index_name = f"history_{index_name}"
        await es.delete(index=prefixed_index_name, id=uid)
        return {"message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{index_name}/items/{uid}")
async def update_history_item(index_name: str, uid: str, item: HistoryItem):
    es = await ElasticsearchClient.get_client()
    try:
        # 添加前缀
        prefixed_index_name = f"history_{index_name}"
        await es.update(
            index=prefixed_index_name,
            id=uid,
            doc=item.model_dump()
        )
        return {"message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 