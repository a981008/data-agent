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
| `MYSQL_USER` | MySQL 应用用户名 | `your_user_here` |
| `MYSQL_PASSWORD` | MySQL 应用用户密码 | `your_password_here` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | `your_api_key_here` |
| `COMPOSE_FILE` | docker-compose 配置文件路径 | `docker/docker-compose.yaml` |

## 项目结构

```
src/
├── client/              # 服务客户端封装
│   ├── mysql_client.py      # MySQL ORM 客户端
│   ├── embedding_client.py  # Embedding 服务客户端
│   ├── es_client.py         # Elasticsearch 客户端
│   └── milvus_client.py     # Milvus 向量数据库客户端
├── conf/               # 配置模块
│   ├── app_config.py        # 应用配置（DBConfig, MilvusConfig 等）
│   ├── config_loader.py     # YAML 配置加载器
│   └── meta_config.py       # 元数据配置
├── core/                # 核心模块
│   └── log.py                # 日志封装
├── entity/              # 数据实体
│   └── meta_entity.py       # ColumnInfo, ColumnMetric, MetricInfo, TableInfo, ValueInfo
├── model/               # ORM 模型（meta 库）
│   ├── base.py              # SQLAlchemy 基类
│   ├── table_info.py        # 表元数据 ORM
│   ├── column_info.py       # 列元数据 ORM
│   ├── metric_info.py       # 指标信息 ORM
│   └── column_metric.py     # 列-指标关联 ORM
├── repo/                # 数据访问层
│   ├── meta_mysql_repository.py  # meta 库访问
│   ├── dw_mysql_repository.py    # dw 库访问
│   └── mapper.py                  # 数据映射
├── service/             # 业务逻辑层
│   └── meta_knowledge_service.py  # 元数据知识服务
└── script/              # 独立脚本
    └── build_meta_knowledge.py    # 构建元数据知识库
```

## 初始化配置

### MySQL

MySQL 容器启动时自动执行 `docker/mysql` 目录下的 SQL 脚本：

| 文件 | 顺序 | 作用 |
|------|------|------|
| `01-dw.sql` | 1 | 创建 `dw` 数据库及事实/维度表 |
| `02-meta.sql` | 2 | 创建 `meta` 数据库及元数据表 |
| `03-grant.sh` | 3 | 授权应用用户访问 `dw` 和 `meta` 数据库 |

### Milvus

配置文件位于 `docker/milvus/`：
- **embedEtcd.yaml** — 嵌入式 etcd 配置
- **user.yaml** — 自定义覆盖配置

## 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 启动指定服务
docker-compose up -d mysql elasticsearch milvus

# 停止服务
docker-compose stop

# 销毁服务（保留数据卷）
docker-compose down

# 销毁服务（删除数据卷）
docker-compose down -v
```

## 服务访问

| 服务 | 地址 |
|------|------|
| MySQL | localhost:3306 |
| Elasticsearch | http://localhost:9200 |
| Kibana | http://localhost:5601 |
| Embedding | http://localhost:8081 |
| Milvus | localhost:19530 |
| Attu | http://localhost:3000 |