from pymilvus import AsyncMilvusClient, DataType

from src.core.log import get_logger

logger = get_logger(__name__)


class ColumnMilvusRepository:
    collection_name = "column_info"

    def __init__(self, client: AsyncMilvusClient, embedding_size):
        self.client = client
        self.embedding_size = embedding_size

    async def ensure_collection(self):
        if await self.client.has_collection(self.collection_name):
            await self.client.drop_collection(self.collection_name)
            logger.info(f"Dropped existing collection '{self.collection_name}'")

        schema = self.client.create_schema(
            auto_id=False,
            enable_dynamic_field=True,
        )
        schema.add_field(
            field_name="id", datatype=DataType.VARCHAR, max_length=256, is_primary=True
        )
        schema.add_field(
            field_name="embedding",
            datatype=DataType.FLOAT_VECTOR,
            dim=self.embedding_size,
        )
        schema.add_field(field_name="payload", datatype=DataType.JSON)

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 128},
        )

        await self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
            lazy_load=True,
        )
        logger.info(
            f"Collection '{self.collection_name}' created with embedding size {self.embedding_size}"
        )

    async def save_column_embeddings(self, columns: list[dict], batch_size=500):
        if not columns:
            return

        total = len(columns)
        for i in range(0, total, batch_size):
            batch = columns[i : i + batch_size]
            await self.client.insert(
                collection_name=self.collection_name,
                data=batch,
            )
            logger.info(f"Saved batch {i//batch_size + 1}: {len(batch)} columns")
        logger.info(f"Saved {total} column embeddings to Milvus")

    async def search_columns(
        self, query_embedding: list[float], limit: int = 5
    ) -> list[dict]:
        results = await self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            limit=limit,
            output_fields=["id", "payload"],
        )

        matches = []
        for hits in results:
            for hit in hits:
                matches.append(
                    {
                        "id": hit["id"],
                        "payload": hit.get("payload", {}),
                        "distance": hit["distance"],
                    }
                )
        return matches

    async def load_collection(self):
        await self.client.load_collection(self.collection_name)

    async def delete_all(self):
        if await self.client.has_collection(self.collection_name):
            await self.client.drop_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' dropped")
