from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List, Optional
from .database.config import RedisConfig, DatabaseManager
from .database.operator import RedisOperator
from .database.vector_search import vector_searcher
from .database.model_config import ModelConfig, ModelManager
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置相关接口
@app.post("/database/config")
async def create_db_config(config: RedisConfig):
    """创建或更新数据库配置"""
    try:
        configs = DatabaseManager.load_configs()
        
        # 保存配置，使用name作为键
        configs[config.name] = config.dict()
        DatabaseManager.save_configs(configs)
        
        return {
            "message": "Redis配置已成功保存",
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置时出错: {str(e)}")

@app.get("/database/configs")
async def get_db_configs():
    """获取所有配置名称列表"""
    try:
        configs = DatabaseManager.load_configs()
        return {"names": list(configs.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取配置时出错: {str(e)}")

@app.get("/database/config/{name}")
async def get_db_config(name: str):
    """获取指定名称的配置详情"""
    try:
        configs = DatabaseManager.load_configs()
        if name not in configs:
            raise HTTPException(status_code=404, detail="配置不存在")
        return {"config": configs[name]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取配置时出错: {str(e)}")

# 数据管理相关接口
@app.post("/data/{config_name}/{key}")
async def create_data(
    config_name: str, 
    key: str,
    data: Dict[str, Any]
):
    """创建数据"""
    try:
        configs = DatabaseManager.load_configs()
        if config_name not in configs:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        config = RedisConfig(**configs[config_name])
        operator = RedisOperator(config)
        
        success = await operator.create(key, data)
        if not success:
            raise HTTPException(status_code=500, detail="创建数据失败")
            
        return {"message": "数据创建成功"}
    except HTTPException:
        raise
    except Exception as e:
        # 添加错误日志以便调试
        print(f"创建数据时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建数据时出错: {str(e)}")

@app.get("/data/{config_name}/{key}")
async def get_data(config_name: str, key: str):
    try:
        configs = DatabaseManager.load_configs()
        if config_name not in configs:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        config = RedisConfig(**configs[config_name])
        operator = RedisOperator(config)
        
        data = await operator.get(key)
        if data is None:
            raise HTTPException(status_code=404, detail="数据不存在")
            
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据时出错: {str(e)}")

@app.put("/data/{config_name}/{key}")
async def update_data(config_name: str, key: str, data: Dict[str, Any]):
    try:
        configs = DatabaseManager.load_configs()
        if config_name not in configs:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        config = RedisConfig(**configs[config_name])
        operator = RedisOperator(config)
        
        success = await operator.update(key, data)
        if not success:
            raise HTTPException(status_code=404, detail="数据不存在或更新失败")
            
        return {"message": "数据更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新数据时出错: {str(e)}")

@app.delete("/data/{config_name}/{key}")
async def delete_data(config_name: str, key: str):
    try:
        configs = DatabaseManager.load_configs()
        if config_name not in configs:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        config = RedisConfig(**configs[config_name])
        operator = RedisOperator(config)
        
        success = await operator.delete(key)
        if not success:
            raise HTTPException(status_code=404, detail="数据不存在")
            
        return {"message": "数据删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除数据时出错: {str(e)}")

@app.get("/data/{config_name}")
async def list_data(config_name: str, pattern: str = "*"):
    try:
        configs = DatabaseManager.load_configs()
        if config_name not in configs:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        config = RedisConfig(**configs[config_name])
        operator = RedisOperator(config)
        
        keys = await operator.list_keys(pattern)
        return {"keys": keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出数据时出错: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    await DatabaseManager.close_connection() 

# 添加以下批量操作接口
@app.get("/export/{config_name}")
async def export_data(
    config_name: str,
    pattern: str = "*"
):
    """导出数据"""
    try:
        configs = DatabaseManager.load_configs()
        if config_name not in configs:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        config = RedisConfig(**configs[config_name])
        operator = RedisOperator(config)
        
        # 获取导出数据
        data = await operator.export_data(pattern)
        
        # 确保返回的是可序列化的数据
        return {"data": data}
    except Exception as e:
        print(f"导出数据时出错: {str(e)}")  # 添加错误日志
        raise HTTPException(status_code=500, detail=f"导出数据时出错: {str(e)}")

@app.post("/database/config/delete")
async def delete_db_config(data: Dict[str, str]):
    """删除数据库配置"""
    try:
        name = data.get("name")
        if not name:
            raise HTTPException(status_code=400, detail="配置名称不能为空")
        
        configs = DatabaseManager.load_configs()
        if name not in configs:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 删除配置
        del configs[name]
        DatabaseManager.save_configs(configs)
        
        return {"message": f"配置 {name} 已成功删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除配置时出错: {str(e)}") 

# 修改搜索接口
@app.get("/search/{config_name}")
async def search_data(
    config_name: str,
    collection_key: str,  # 集合键名参数
    query: str,
    top_k: Optional[int] = 5,
    threshold: Optional[float] = 0.5,
    search_key: Optional[bool] = True  # 添加参数控制搜索目标
):
    """
    搜索数据
    :param config_name: 配置名称
    :param collection_key: 集合键名
    :param query: 搜索查询
    :param top_k: 返回结果数量
    :param threshold: 相似度阈值
    :param search_key: 是否搜索键名
    """
    try:
        configs = DatabaseManager.load_configs()
        if config_name not in configs:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        config = RedisConfig(**configs[config_name])
        operator = RedisOperator(config)
        
        # 获取指定集合的数据
        collection_data = await operator.get(collection_key)
        if not collection_data:
            return {"results": []}
            
        # 执行向量搜索
        results = vector_searcher.search(
            query=query,
            data_dict=collection_data,
            top_k=top_k,
            threshold=threshold,
            search_key=search_key  # 传递搜索目标参数
        )
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索数据时出错: {str(e)}")

# 添加模型管理相关接口
@app.post("/model/config")
async def create_model_config(config: ModelConfig):
    """创建或更新模型配置"""
    try:
        configs = ModelManager.load_configs()
        configs[config.name] = config.dict()
        ModelManager.save_configs(configs)
        return {
            "message": "模型配置已成功保存",
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置时出错: {str(e)}")

@app.get("/model/configs")
async def get_model_configs():
    """获取所有模型配置"""
    try:
        configs = ModelManager.load_configs()
        return {"configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取配置时出错: {str(e)}")

@app.post("/model/config/delete")
async def delete_model_config(data: Dict[str, str]):
    """删除模型配置"""
    try:
        name = data.get("name")
        if not name:
            raise HTTPException(status_code=400, detail="配置名称不能为空")
        
        success = ModelManager.delete_model_config(name)
        if not success:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        return {"message": f"配置 {name} 已成功删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除配置时出错: {str(e)}")

# 添加以下接口
@app.get("/model/current")
async def get_current_model():
    """获取当前选择的模型配置"""
    try:
        current_model = ModelManager.get_current_model()
        if not current_model:
            raise HTTPException(status_code=404, detail="未选择模型")
        return {"model": current_model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取当前模型时出错: {str(e)}")

@app.post("/model/current/{name}")
async def set_current_model(name: str):
    """设置当前选择的模型"""
    try:
        success = ModelManager.set_current_model(name)
        if not success:
            raise HTTPException(status_code=404, detail="模型配置不存在")
        return {"message": f"已选择模型: {name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置当前模型时出错: {str(e)}") 