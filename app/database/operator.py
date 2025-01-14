from typing import Optional, Dict, Any, List
import json
from .config import RedisConfig, DatabaseManager

class RedisOperator:
    def __init__(self, config: RedisConfig):
        self.config = config

    async def _get_connection(self):
        return await DatabaseManager.get_redis_connection(self.config)

    async def create(self, key: str, data: Dict[str, Any]) -> bool:
        """
        创建数据
        :param key: Redis键
        :param data: 要存储的数据
        :return: 是否创建成功
        """
        redis_client = await self._get_connection()
        try:
            # 将字典转换为JSON字符串存储
            success = await redis_client.set(key, json.dumps(data, ensure_ascii=False))
            return success
        except Exception as e:
            print(f"创建数据时出错: {str(e)}")
            return False

    async def get(self, key: str) -> Optional[Dict]:
        """
        获取数据
        :param key: Redis键
        :return: 存储的数据或None
        """
        redis_client = await self._get_connection()
        try:
            data = await redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"获取数据时出错: {str(e)}")
            return None

    async def update(self, key: str, data: Dict[str, Any]) -> bool:
        """
        更新数据，将新数据与已有数据合并
        :param key: Redis键
        :param data: 新的数据
        :return: 是否更新成功
        """
        redis_client = await self._get_connection()
        try:
            # 检查键是否存在
            if not await redis_client.exists(key):
                return False
            
            # 获取已有数据
            existing_data = await self.get(key)
            if existing_data is None:
                return False
            
            # 合并数据：将新数据更新到已有数据中
            merged_data = {**existing_data, **data}
            
            # 保存合并后的数据
            success = await redis_client.set(key, json.dumps(merged_data, ensure_ascii=False))
            return success
        except Exception as e:
            print(f"更新数据时出错: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """
        删除数据
        :param key: Redis键
        :return: 是否删除成功
        """
        redis_client = await self._get_connection()
        try:
            return await redis_client.delete(key) > 0
        except Exception as e:
            print(f"删除数据时出错: {str(e)}")
            return False

    async def list_keys(self, pattern: str = "*") -> List[str]:
        """
        列出所有匹配的键
        :param pattern: 匹配模式
        :return: 键列表
        """
        redis_client = await self._get_connection()
        try:
            return await redis_client.keys(pattern)
        except Exception as e:
            print(f"列出键时出错: {str(e)}")
            return [] 

    async def export_data(self, pattern: str = "*") -> Dict[str, Any]:
        """
        导出数据
        :param pattern: 匹配模式
        :return: {key: data} 的字典
        """
        redis_client = await self._get_connection()
        try:
            # 获取所有匹配的键
            keys = await redis_client.keys(pattern)
            if not keys:
                return {}
            
            # 使用pipeline批量获取数据
            pipe = redis_client.pipeline()
            for key in keys:
                pipe.get(key)
            
            values = await pipe.execute()
            
            # 将结果组织成字典
            result = {}
            for key, value in zip(keys, values):
                try:
                    if value is not None:
                        # 尝试解析JSON
                        try:
                            result[key] = json.loads(value)
                        except json.JSONDecodeError:
                            # 如果不是JSON格式，则保存原始值
                            result[key] = value
                except Exception as e:
                    print(f"处理键 {key} 时出错: {str(e)}")
                    continue
            
            return result
        except Exception as e:
            print(f"导出数据时出错: {str(e)}")
            return {} 