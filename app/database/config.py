from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os
import redis.asyncio as redis

class RedisConfig(BaseModel):
    name: str  # 配置名称
    host: str
    port: int
    db: int = 0  # 默认使用 db 0

class DatabaseManager:
    CONFIG_FILE = "database_configs.json"
    _redis_client: Optional[redis.Redis] = None
    
    @staticmethod
    def load_configs() -> Dict[str, Dict]:
        """加载所有配置，返回 {name: config} 的字典"""
        try:
            if os.path.exists(DatabaseManager.CONFIG_FILE):
                with open(DatabaseManager.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    configs = json.load(f)
                    # 确保加载的是字典格式
                    if isinstance(configs, list):
                        # 如果是旧格式（列表），转换为新格式（字典）
                        return {item['name']: item for item in configs}
                    # 移除所有密码字段
                    for config in configs.values():
                        if 'password' in config:
                            del config['password']
                    return configs
        except Exception as e:
            print(f"加载配置时出错: {str(e)}")
        return {}

    @staticmethod
    def save_configs(configs: Dict[str, Dict]) -> None:
        """保存配置字典到文件"""
        try:
            # 确保不保存密码字段
            configs_to_save = {}
            for name, config in configs.items():
                config_copy = config.copy()
                if 'password' in config_copy:
                    del config_copy['password']
                configs_to_save[name] = config_copy

            with open(DatabaseManager.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(configs_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置时出错: {str(e)}")
            raise

    @classmethod
    async def get_redis_connection(cls, config: RedisConfig) -> redis.Redis:
        if cls._redis_client is None:
            cls._redis_client = redis.Redis(
                host=config.host,
                port=config.port,
                db=config.db,
                decode_responses=True
            )
        return cls._redis_client

    @classmethod
    async def close_connection(cls):
        if cls._redis_client is not None:
            await cls._redis_client.close()
            cls._redis_client = None 