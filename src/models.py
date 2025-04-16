from pydantic import BaseModel
from typing import List, Optional
import uuid

class Test(BaseModel):
    test_result: str
    target_result: str
    error_info: str

class PredefinedItem(BaseModel):
    name: str
    question: str

class HistoryItem(BaseModel):
    name: str
    question: str
    code: str

class TaskItem(BaseModel):
    name: str
    progress: str
    num_tests: int
    pass_rate: float
    cover_rate: float
    question: str
    code: str
    tests: List[Test]

class RetrievalItem(BaseModel):
    code: str
    desc: str

class VectorSearchRequest(BaseModel):
    query_vector: List[float]
    top_k: int

class IndexMetadata(BaseModel):
    name: str
    type: str  # predefined, history, task, retrieval 