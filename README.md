# Data Agent

RAG/向量检索项目的开发环境，包含结构化数据存储、全文检索、向量存储和 Embedding 服务。

## 服务架构

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| MySQL | mysql:8.0 | 3306 | 结构化数据存储，utf8mb4 字符集 |
| Elasticsearch | elasticsearch:8.19.0 | 9200 | 全文检索引擎，单节点模式 |
| Kibana | kibana:8.19.10 | 5601 | Elasticsearch 可视化 |
| Qdrant | qdrant/qdrant:v1.16 | 6333/6334 | 向量数据库 |
| Embedding | huggingface text-embeddings-inference | 8081 | 中文 Embedding 模型 (bge-large-zh-v1.5) |

## 快速启动

```bash
docker-compose up -d
```

## 初始化

MySQL 容器启动时自动执行 `docker/mysql` 目录下的 SQL 脚本进行数据库初始化。

docker-compose.yaml 中配置了挂载： 

```yaml
volumes:
    - ./mysql:/docker-entrypoint-initdb.d
```               

docker-entrypoint-initdb.d 是 MySQL 官方镜像保留的初始化目录，容器首次启动时自动执行该目录下的 .sql、.sql.gz、.sh 脚本

## 服务管理

```bash
# 启动服务
docker-compose up -d

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
- **Qdrant**: http://localhost:6333
- **Embedding**: http://localhost:8081

## 单元测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行指定测试文件
uv run pytest tests/conf/test_config_loader.py -v

# 运行指定测试类
uv run pytest tests/conf/test_config_loader.py::TestConfigLoader -v
```

### 测试覆盖

| 文件 | 覆盖模块 |
|------|----------|
| test_entities.py | TableInfo, ColumnInfo, MetricInfo, ValueInfo |
| test_config_loader.py | load_config 配置加载 |
| test_prompt_loader.py | load_prompt 提示词加载 |
| test_state.py | TypedDict 状态类型 |
| test_context.py | ContextVar 请求上下文 |
| test_base.py | SQLAlchemy Base |
