from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import json

class VectorSearcher:
    def __init__(self):
        # 使用多语言模型以支持中英文
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
    def text_to_vector(self, text: str) -> np.ndarray:
        """将文本转换为向量"""
        return self.model.encode(text, convert_to_tensor=False)
    
    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算两个向量的余弦相似度"""
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    
    def search(self, 
              query: str, 
              data_dict: Dict[str, Any], 
              top_k: int = 5, 
              threshold: float = 0.5,
              search_key: bool = True  # 添加参数控制搜索目标
    ) -> List[Dict[str, Any]]:
        """
        在数据中搜索与查询最相似的内容
        :param query: 查询文本
        :param data_dict: 要搜索的数据字典
        :param top_k: 返回的最大结果数
        :param threshold: 相似度阈值
        :param search_key: 是否搜索键名（True）或值（False）
        :return: 相似度排序后的结果列表
        """
        query_vector = self.text_to_vector(query)
        results = []
        
        for key, value in data_dict.items():
            # 根据 search_key 参数决定搜索目标
            if search_key:
                # 搜索键名
                target_text = key
            else:
                # 搜索值
                target_text = json.dumps(value, ensure_ascii=False)
            
            target_vector = self.text_to_vector(target_text)
            similarity = self.calculate_similarity(query_vector, target_vector)
            
            if similarity >= threshold:
                results.append({
                    'key': key,
                    'data': value,
                    'similarity': similarity
                })
        
        # 按相似度降序排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

# 创建全局搜索器实例
vector_searcher = VectorSearcher() 