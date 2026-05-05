from elasticsearch import AsyncElasticsearch
from typing import Optional

from src.conf.app_config import ESConfig
from src.core.log import get_logger

logger = get_logger(__name__)


class ESClientManager:
    def __init__(self, config: ESConfig):
        self.config: ESConfig = config
        self._client: Optional[AsyncElasticsearch] = None

    def _get_url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    async def connect(self):
        if self._client is None:
            try:
                self._client = AsyncElasticsearch(hosts=[self._get_url()])
                logger.info(f"Connected to Elasticsearch at {self._get_url()}")
            except Exception as e:
                logger.error(f"Failed to connect to Elasticsearch: {e}")
                raise

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self.close()
        return False

    def client(self) -> AsyncElasticsearch:
        if self._client is not None:
            return self._client
        raise ConnectionError("Elasticsearch client is not connected")

    async def close(self):
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("Elasticsearch connection closed")


if __name__ == "__main__":
    import asyncio

    async def test_es_client():
        from src.conf.app_config import app_config

        async with ESClientManager(app_config.es) as manager:
            client = manager.client()

            # 获取集群健康状态
            health = await client.cluster.health()
            logger.info(f"集群状态: {health['status']}, 节点数: {health['number_of_nodes']}")

            # 创建测试索引（如果不存在）
            index_name = "test_index"
            exists = await client.indices.exists(index=index_name)
            if not exists:
                await client.indices.create(
                    index=index_name,
                    body={
                        "mappings": {
                            "properties": {
                                "title": {"type": "text"},
                                "content": {"type": "text"},
                            }
                        }
                    },
                )
                logger.info(f"索引 {index_name} 创建成功")

            # 插入一条文档
            await client.index(index=index_name, id="1", document={"title": "测试文档", "content": "这是一条测试内容"})
            await client.indices.refresh(index=index_name)

            # 搜索文档
            result = await client.search(index=index_name, body={"query": {"match": {"content": "测试"}}})
            logger.info(f"搜索结果数: {result['hits']['total']['value']}")
            for hit in result["hits"]["hits"]:
                logger.info(f"  - {hit['_source']}")

            # 删除测试索引
            await client.indices.delete(index=index_name)
            logger.info(f"索引 {index_name} 已删除")

    asyncio.run(test_es_client())
