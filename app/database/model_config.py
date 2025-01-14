from pydantic import BaseModel
import json
import os
from typing import Optional, Dict

class ModelConfig(BaseModel):
    name: str
    url: str
    api_key: str
    model_type: str  # 'chat' 或 'embedding'

class ModelManager:
    CONFIG_FILE = "model_configs.json"
    CURRENT_MODEL_FILE = "current_model.json"
    
    @staticmethod
    def load_configs() -> Dict[str, Dict]:
        """加载所有模型配置"""
        try:
            if os.path.exists(ModelManager.CONFIG_FILE):
                with open(ModelManager.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    configs = json.load(f)
                    # 移除所有密钥字段
                    for config in configs.values():
                        if 'api_key' in config:
                            del config['api_key']
                    return configs
        except Exception as e:
            print(f"加载模型配置时出错: {str(e)}")
        return {}

    @staticmethod
    def save_configs(configs: Dict[str, Dict]) -> None:
        """保存所有模型配置"""
        try:
            # 确保不保存密钥字段
            configs_to_save = {}
            for name, config in configs.items():
                config_copy = config.copy()
                if 'api_key' in config_copy:
                    del config_copy['api_key']
                configs_to_save[name] = config_copy

            with open(ModelManager.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(configs_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模型配置时出错: {str(e)}")
            raise

    @staticmethod
    def get_current_model() -> Optional[Dict]:
        """获取当前选择的模型配置"""
        try:
            if os.path.exists(ModelManager.CURRENT_MODEL_FILE):
                with open(ModelManager.CURRENT_MODEL_FILE, 'r', encoding='utf-8') as f:
                    current = json.load(f)
                    # 确保配置仍然存在
                    configs = ModelManager.load_configs()
                    if current['name'] in configs:
                        return {**current, **configs[current['name']]}
        except Exception as e:
            print(f"获取当前模型时出错: {str(e)}")
        return None

    @staticmethod
    def set_current_model(name: str) -> bool:
        """设置当前选择的模型"""
        try:
            configs = ModelManager.load_configs()
            if name not in configs:
                return False
                
            with open(ModelManager.CURRENT_MODEL_FILE, 'w', encoding='utf-8') as f:
                json.dump({'name': name}, f)
            return True
        except Exception as e:
            print(f"设置当前模型时出错: {str(e)}")
            return False 

    @staticmethod
    def delete_model_config(name: str) -> bool:
        """删除模型配置，如果是当前模型则同时清除当前模型"""
        try:
            configs = ModelManager.load_configs()
            if name not in configs:
                return False
            
            # 删除配置
            del configs[name]
            ModelManager.save_configs(configs)
            
            # 如果删除的是当前模型，清除当前模型设置
            if os.path.exists(ModelManager.CURRENT_MODEL_FILE):
                with open(ModelManager.CURRENT_MODEL_FILE, 'r', encoding='utf-8') as f:
                    current = json.load(f)
                    if current.get('name') == name:
                        os.remove(ModelManager.CURRENT_MODEL_FILE)
            
            return True
        except Exception as e:
            print(f"删除模型配置时出错: {str(e)}")
            return False 