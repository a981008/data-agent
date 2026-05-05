from pymilvus import AsyncMilvusClient
from typing import Optional, Any, List, Dict
import asyncio

from src.conf.app_config import MilvusConfig
from src.core.log import get_logger

logger = get_logger(__name__)


class MilvusClientManager:
    def __init__(self, config: MilvusConfig):
        self.config: MilvusConfig = config
        self._client: Optional[AsyncMilvusClient] = None

    def _get_url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    async def connect(self):
        if self._client is None:
            try:
                self._client = AsyncMilvusClient(uri=self._get_url())
                logger.info(f"Connected to Milvus at {self._get_url()}")
            except Exception as e:
                logger.exception(f"Failed to connect to Milvus: {e}")
                raise

    async def __aenter__(self):
        await self.connect()
        return self

    def client(self) -> AsyncMilvusClient:
        if self._client is not None:
            return self._client
        else:
            raise ConnectionError("Milvus client is not connected")

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        await self.close()
        return False

    async def close(self):
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("Milvus connection closed")


if __name__ == "__main__":
    from src.conf.app_config import app_config
    from pymilvus import DataType
    import random

    BATCH_SIZE = 500

    def generate_embeddings(num_vectors, dim=768):
        return [[random.random() for _ in range(dim)] for _ in range(num_vectors)]

    async def test_milvus_client():
        async with MilvusClientManager(app_config.milvus) as manager:
            client = manager.client()
            if not await client.has_collection("products"):
                schema = client.create_schema(
                    auto_id=False,
                    enable_dynamic_field=True,
                )

                schema.add_field(
                    field_name="id", datatype=DataType.INT64, is_primary=True
                )
                schema.add_field(
                    field_name="title", datatype=DataType.VARCHAR, max_length=256
                )
                schema.add_field(
                    field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=768
                )
                schema.add_field(field_name="price", datatype=DataType.FLOAT)

                index_params = client.prepare_index_params()
                index_params.add_index(
                    field_name="embedding",
                    index_type="IVF_FLAT",
                    metric_type="COSINE",
                    params={"nlist": 128},
                )

                await client.create_collection(
                    collection_name="products", schema=schema, index_params=index_params
                )

                large_data = [
                    {
                        "id": i,
                        "embedding": generate_embeddings(1)[0],
                        "title": f"Product {i}",
                        "price": 100.0 + i,
                    }
                    for i in range(10000)
                ]

                total = len(large_data)
                for i in range(0, total, BATCH_SIZE):
                    batch = large_data[i : i + BATCH_SIZE]
                    await client.insert(collection_name="products", data=batch)
                    print(f"已插入 {min(i + BATCH_SIZE, total)}/{total} 条记录")
                print("所有数据插入完成")

            await client.load_collection(collection_name="products")
            status = await client.get_load_state(collection_name="products")
            print(status)

            query_vector = generate_embeddings(1)[0]
            results = await client.search(
                collection_name="products",
                data=[query_vector],
                limit=5,
                output_fields=["title", "price"],
            )

            for i, hits in enumerate(results):
                print(f"查询 {i+1} 的结果:")
                for hit in hits:
                    print(
                        f"  ID: {hit['id']}, 距离: {hit['distance']:.4f}, 标题: {hit['title']}, 价格: ${hit['price']}"
                    )

    asyncio.run(test_milvus_client())
