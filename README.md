# 知识库管理系统

基于FastAPI和Elasticsearch实现的知识库管理系统，支持四种类型的知识库：预设知识库、历史知识库、任务知识库和检索知识库。

## 环境要求

- Python 3.8+
- Elasticsearch 8.x+
- FastAPI
- Uvicorn

## Docker部署
可在docker-compose.yml文件中修改

## 源码安装

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
创建`.env`文件，配置Elasticsearch连接信息：
```
ES_HOST=localhost
ES_PORT=9200
ES_USER=your_username
ES_PASSWORD=your_password
```

## 运行

```bash
uvicorn app:app --reload
```

## API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
kb_new/
├── app.py              # 主应用入口
├── requirements.txt    # 项目依赖
├── README.md          # 项目说明
└── src/               # 源代码目录
    ├── config.py      # 配置文件
    ├── db.py          # 数据库连接
    ├── models.py      # 数据模型
    └── routers/       # 路由模块
        ├── predefined.py
        ├── history.py
        ├── task.py
        └── retrieval.py
```

## 知识库类型

### 1. 预设知识库
- 存储预设问答对
- 包含字段：uid, name, question

### 2. 历史知识库
- 存储历史问答记录
- 包含字段：uid, name, question, code

### 3. 任务知识库
- 存储任务相关信息
- 包含字段：uid, name, progress, num_tests, pass_rate, cover_rate, question, code, tests

### 4. 检索知识库
- 支持向量检索
- 包含字段：uid, code, desc, desc_vector

## 主要功能

1. 知识库管理
   - 创建/删除知识库
   - 列出所有知识库

2. 数据管理
   - 添加/更新/删除数据项
   - 批量导入/导出数据

3. 检索功能
   - 支持向量相似度检索
   - 支持关键词检索

## 注意事项

1. 确保Elasticsearch服务已启动
2. 检索知识库需要预先计算文本向量
3. 建议定期备份重要数据 