from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from ..models import TaskItem, IndexMetadata
from ..db import ElasticsearchClient

router = APIRouter()

@router.get("/list")
async def get_task_list():
    es = await ElasticsearchClient.get_client()
    try:
        indices = await ElasticsearchClient.list_indices_by_type("task")
        return {"indices": indices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{index_name}/items")
async def get_task_items(index_name: str):
    es = await ElasticsearchClient.get_client()
    try:
        # 验证索引类型
        index_type = await ElasticsearchClient.get_index_type(index_name)
        if index_type != "task":
            raise HTTPException(status_code=400, detail="Invalid index type")
            
        result = await es.search(
            index=index_name,
            query={"match_all": {}}
        )
        items = [{
            "uid": hit["_id"],
            "name": hit["_source"]["name"],
            "progress": hit["_source"]["progress"]
        } for hit in result["hits"]["hits"]]
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{index_name}/items/{uid}")
async def get_task_item(index_name: str, uid: str):
    es = await ElasticsearchClient.get_client()
    try:
        # 验证索引类型
        index_type = await ElasticsearchClient.get_index_type(index_name)
        if index_type != "task":
            raise HTTPException(status_code=400, detail="Invalid index type")
            
        result = await es.get(index=index_name, id=uid)
        return result["_source"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{index_name}")
async def create_task_index(index_name: str):
    es = await ElasticsearchClient.get_client()
    try:
        metadata = IndexMetadata(name=index_name, type="task")
        mappings = {
            "name": {"type": "keyword"},
            "progress": {"type": "keyword"},
            "num_tests": {"type": "integer"},
            "pass_rate": {"type": "float"},
            "cover_rate": {"type": "float"},
            "question": {"type": "text"},
            "code": {"type": "text"},
            "tests": {
                "type": "nested",
                "properties": {
                    "test_result": {"type": "text"},
                    "target_result": {"type": "text"},
                    "error_info": {"type": "text"}
                }
            }
        }
        await ElasticsearchClient.create_index(metadata, mappings)
        return {"message": f"Index {index_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{index_name}/items")
async def create_task_item(index_name: str, item: TaskItem):
    es = await ElasticsearchClient.get_client()
    try:
        # 验证索引类型
        index_type = await ElasticsearchClient.get_index_type(index_name)
        if index_type != "task":
            raise HTTPException(status_code=400, detail="Invalid index type")
            
        uid = str(uuid.uuid4())
        await es.index(
            index=index_name,
            id=uid,
            document=item.dict()
        )
        return {"message": "Item created successfully", "uid": uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{index_name}")
async def delete_task_index(index_name: str):
    es = await ElasticsearchClient.get_client()
    try:
        # 验证索引类型
        index_type = await ElasticsearchClient.get_index_type(index_name)
        if index_type != "task":
            raise HTTPException(status_code=400, detail="Invalid index type")
            
        await ElasticsearchClient.delete_index(index_name)
        return {"message": f"Index {index_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{index_name}/items/{uid}")
async def delete_task_item(index_name: str, uid: str):
    es = await ElasticsearchClient.get_client()
    try:
        # 验证索引类型
        index_type = await ElasticsearchClient.get_index_type(index_name)
        if index_type != "task":
            raise HTTPException(status_code=400, detail="Invalid index type")
            
        await es.delete(index=index_name, id=uid)
        return {"message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{index_name}/items/{uid}")
async def update_task_item(index_name: str, uid: str, item: TaskItem):
    es = await ElasticsearchClient.get_client()
    try:
        # 验证索引类型
        index_type = await ElasticsearchClient.get_index_type(index_name)
        if index_type != "task":
            raise HTTPException(status_code=400, detail="Invalid index type")
            
        await es.update(
            index=index_name,
            id=uid,
            doc=item.dict()
        )
        return {"message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{index_name}/items/{uid}/tests")
async def update_task_tests(index_name: str, uid: str, tests: List[dict]):
    es = await ElasticsearchClient.get_client()
    try:
        # 验证索引类型
        index_type = await ElasticsearchClient.get_index_type(index_name)
        if index_type != "task":
            raise HTTPException(status_code=400, detail="Invalid index type")
            
        await es.update(
            index=index_name,
            id=uid,
            doc={"tests": tests}
        )
        return {"message": "Tests updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 