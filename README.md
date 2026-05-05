# Data Agent

RAG/向量检索项目的开发环境，包含结构化数据存储、全文检索、向量存储和 Embedding 服务。

## 服务架构

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| MySQL | mysql:8.0 | 3306 | 结构化数据存储，utf8mb4 字符集 |
| Elasticsearch | elasticsearch:8.19.0 | 9200 | 全文检索引擎，单节点模式 |
| Kibana | kibana:8.19.10 | 5601 | Elasticsearch 可视化 |
| Embedding | huggingface text-embeddings-inference | 8081 | 中文 Embedding 模型 (bge-large-zh-v1.5) |
| Milvus | milvusdb/milvus:v2.6.14 | 19530/9091/2379 | 向量数据库（嵌入式 etcd） |
| Attu | zilliz/attu:v3.0.0-beta.1 | 3000 | Milvus 可视化管理平台 |

## 快速启动

复制 `.env.example` 为 `.env`，修改其中配置后启动：

```bash
cp .env.example .env
# 编辑 .env 中的 MYSQL_ROOT_PASSWORD、MYSQL_PASSWORD、OPENAI_API_KEY 等
docker-compose up -d
```

### 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `MYSQL_ROOT_PASSWORD` | MySQL root 密码 | `your_root_password_here` |
| `MYSQL_PASSWORD` | MySQL data_agent 用户密码 | `your_password_here` |
| `MYSQL_USER` | MySQL 应用用户名 | `your_user_here` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | `your_api_key_here` |
| `COMPOSE_FILE` | docker-compose 配置文件路径 | `docker/docker-compose.yaml` |

## 项目结构

```
src/
├── client/          # 各服务的客户端封装
│   ├── mysql_client.py       # MySQL ORM 客户端
│   ├── embedding_client.py   # Embedding 服务客户端
│   ├── es_client.py          # Elasticsearch 客户端
│   └── milvus_client.py      # Milvus 向量数据库客户端
├── conf/           # 配置模块
│   ├── app_config.py         # 应用配置（DBConfig, MilvusConfig 等）
│   └── config_loader.py       # YAML 配置加载器
├── model/          # ORM 模型（meta 库）
│   ├── table_info.py          # 表元数据
│   ├── column_info.py         # 列元数据
│   ├── metric_info.py         # 指标信息
│   └── column_metric.py       # 列-指标关联
└── core/           # 核心模块
    └── log.py               # 日志封装
```

## 客户端使用示例

### MySQL

```python
from src.client.mysql_client import MySQLClientManager
from src.conf.app_config import app_config

# 查询 dw 库
async with MySQLClientManager(app_config.db_dw) as mysql_client:
    sf = mysql_client.session()
    async with sf() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM fact_order"))
        print(f"订单总数: {result.scalar()}")

# 查询 meta 库
async with MySQLClientManager(app_config.db_meta) as mysql_client:
    sf = mysql_client.session()
    async with sf() as session:
        result = await session.execute(text("SHOW TABLES"))
        print(f"表列表: {[r[0] for r in result.fetchall()]}")
```

### Embedding

```python
from src.client.embedding_client import EmbeddingClientManager
from src.conf.app_config import app_config

async with EmbeddingClientManager(app_config.embedding) as manager:
    client = manager.client()
    response = await client.post("/embeddings", json={"input": "今天天气不错"})
    result = response.json()
    embedding = result["data"][0]["embedding"]
    print(f"向量维度: {len(embedding)}")
```

### Elasticsearch

```python
from src.client.es_client import ESClientManager
from src.conf.app_config import app_config

async with ESClientManager(app_config.es) as manager:
    client = manager.client()
    health = await client.cluster.health()
    print(f"集群状态: {health['status']}")
    # 创建索引、插入文档、搜索等
```

### Milvus

```python
from src.client.milvus_client import MilvusClientManager
from src.conf.app_config import app_config

async with MilvusClientManager(app_config.milvus) as manager:
    client = manager.client()
    # 创建集合、插入向量、相似度搜索等
```

## 初始化

### MySQL 配置

MySQL 容器启动时自动执行 `docker/mysql` 目录下的 SQL 脚本进行数据库初始化。

docker-compose.yaml 中配置了挂载：

```yaml
volumes:
    - ./mysql:/docker-entrypoint-initdb.d
```

`docker-entrypoint-initdb.d` 是 MySQL 官方镜像保留的初始化目录，容器首次启动时自动执行该目录下的 `.sql`、`.sql.gz`、`.sh` 脚本，按文件名升序执行。

| 文件 | 顺序 | 作用 |
|------|------|------|
| `01-dw.sql` | 1 | 创建 `dw` 数据库及事实/维度表（fact_order, dim_customer 等） |
| `02-meta.sql` | 2 | 创建 `meta` 数据库及元数据表（table_info, column_info 等） |
| `03-grant.sh` | 3 | 授权 `data_agent` 用户访问 `dw` 和 `meta` 数据库 |

### Milvus 配置

Milvus 使用嵌入式 etcd，配置文件位于 `docker/milvus/` 目录：

- **embedEtcd.yaml**: 嵌入式 etcd 配置
- **user.yaml**: 自定义覆盖配置

## 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 启动指定服务
docker-compose up -d mysql
docker-compose up -d elasticsearch
docker-compose up -d embedding
docker-compose up -d milvus

# 停止服务
docker-compose stop

# 销毁服务（删除容器，数据卷保留）
docker-compose down

# 销毁服务（删除容器和数据卷）
docker-compose down -v
```

## 服务访问

- **MySQL**: localhost:3306
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601
- **Embedding**: http://localhost:8081
- **Milvus**: localhost:19530
- **Attu**: http://localhost:3000

## 单元测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行指定测试文件
pytest tests/model/test_meta_models.py -v

# 运行指定测试类
pytest tests/model/test_meta_models.py::TestColumnInfo -v
```

### 测试覆盖

| 文件 | 覆盖模块 |
|------|----------|
| tests/model/test_meta_models.py | TableInfo, ColumnInfo, MetricInfo, ColumnMetric ORM 及关系 |