import httpx
from typing import Optional

from src.conf.app_config import EmbeddingConfig
from src.core.log import get_logger

logger = get_logger(__name__)


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.config: EmbeddingConfig = config
        self._client: Optional[httpx.AsyncClient] = None

    def _get_url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    async def connect(self):
        if self._client is None:
            try:
                self._client = httpx.AsyncClient(base_url=self._get_url(), timeout=30.0)
                logger.info(f"Embedding client connected to {self._get_url()}")
            except Exception as e:
                logger.error(f"Failed to connect to embedding service: {e}")
                raise

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self.close()
        return False

    def client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        raise ConnectionError("Embedding client is not connected")

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("Embedding connection closed")

    async def embed_batch(self, texts: list[str], batch_size=20) -> list[list[float]]:
        if not texts:
            return []

        client = self.client()
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = await client.post(
                "/embeddings",
                json={"input": batch},
            )
            result = response.json()
            all_embeddings.extend([item["embedding"] for item in result["data"]])
        return all_embeddings


if __name__ == "__main__":
    import asyncio

    async def test_embedding_client():
        from src.conf.app_config import app_config

        async with EmbeddingClientManager(app_config.embedding) as manager:
            client = manager.client()

            # 调用 embedding 服务生成向量
            response = await client.post(
                "/embeddings",
                json={
                    "input": "今天天气不错",
                },
            )
            result = response.json()
            embedding = result["data"][0]["embedding"]
            logger.info(f"Embedding 向量维度: {len(embedding)}")
            logger.info(f"Embedding 向量前5维: {embedding[:5]}")

    asyncio.run(test_embedding_client())
