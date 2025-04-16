from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import predefined, history, task, retrieval
from src.config import settings

app = FastAPI(title="知识库管理系统")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(predefined.router, prefix="/api/predefined", tags=["预设知识库"])
app.include_router(history.router, prefix="/api/history", tags=["历史知识库"])
app.include_router(task.router, prefix="/api/task", tags=["任务知识库"])
app.include_router(retrieval.router, prefix="/api/retrieval", tags=["检索知识库"])

@app.get("/")
async def root():
    return {"message": "知识库管理系统API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 