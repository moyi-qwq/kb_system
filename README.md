# AI 知识库管理系统

这是一个基于 FastAPI 和 Redis 的知识库管理系统，支持向量检索和模型管理功能。

## 功能特点

- 支持多个 Redis 数据库的配置和管理
- 基于向量相似度的知识检索
- AI 模型配置管理
- RESTful API 接口
- 支持问答对的增删改查

## 快速开始

### 环境要求

- Python 3.8+
- Redis 服务器
- 足够的内存用于向量计算

### 安装

克隆项目并安装依赖：
```bash
git clone https://github.com/ILSparkle/kb_system.git
cd kb_system
pip install -r requirements.txt
```
启动后端服务
```bash
uvicorn app.main:app --reload --port 8000
```
启动前端服务（可选）
```bash
python serve.py
```

## API 接口说明

### 数据库管理接口

#### 配置管理
- `POST /database/config` - 创建/更新数据库配置
- `GET /database/configs` - 获取所有配置列表
- `GET /database/config/{name}` - 获取指定配置详情
- `POST /database/config/delete` - 删除数据库配置

#### 数据操作
- `POST /data/{config_name}/{key}` - 创建数据
- `GET /data/{config_name}/{key}` - 获取数据
- `PUT /data/{config_name}/{key}` - 更新数据
- `DELETE /data/{config_name}/{key}` - 删除数据
- `GET /data/{config_name}` - 列出所有键
- `GET /export/{config_name}` - 导出数据

#### 向量搜索
- `GET /search/{config_name}` - 搜索数据
  - 参数：
    - `collection_key`: 知识库名称
    - `query`: 搜索文本
    - `top_k`: 返回结果数量
    - `threshold`: 相似度阈值
    - `search_key`: 是否搜索问题（默认为 true）

### 模型管理接口

- `POST /model/config` - 创建/更新模型配置
- `GET /model/configs` - 获取所有模型配置
- `POST /model/config/delete` - 删除模型配置
- `GET /model/current` - 获取当前选择的模型
- `POST /model/current/{name}` - 设置当前模型

## 数据结构

### Redis 配置
```json
{
"name": "配置名称",
"host": "Redis主机地址",
"port": 6379,
"db": 0
}
```

### 模型配置
```json
{
"name": "模型名称",
"url": "API地址",
"api_key": "密钥",
"model_type": "chat/embedding"
}
```

### 知识库数据
```json
{
"问题1": "回答1",
"问题2": "回答2"
}
```

## 前后端连接

前端通过 axios 与后端 API 进行通信。主要连接逻辑：

1. 数据库管理：
   - 前端保存最后选择的配置在 localStorage
   - 启动时自动加载并选择上次的配置
   - 实时同步数据库操作结果

2. 模型管理：
   - 后端维护当前选择的模型状态
   - 前端可以获取和切换当前模型
   - 模型配置中的 API 密钥在传输和显示时做脱敏处理

3. 知识库操作：
   - 支持批量导入和单条添加
   - 编辑时支持同时修改问题和回答
   - 删除操作需要确认
