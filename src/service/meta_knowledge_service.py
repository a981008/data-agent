import uuid
from pathlib import Path
from src.conf.config_loader import load_config
from src.conf.meta_config import MetaConfig
from src.repo.meta_mysql_repository import MetaMySQLRepository
from src.repo.dw_mysql_repository import DwMySQLRepository
from src.core.log import get_logger
from src.entity.meta_entity import ColumnInfo, TableInfo
from src.repo.column_milvus_repository import ColumnMilvusRepository
from src.repo.mapper import Mapper
from src.client.embedding_client import EmbeddingClientManager

logger = get_logger(__name__)


class MetaKnowledgeService:
    def __init__(
        self,
        embedding_client: EmbeddingClientManager,
        meta_mysql_repository: MetaMySQLRepository,
        dw_mysql_repository: DwMySQLRepository,
        column_milvus_repository: ColumnMilvusRepository,
    ):
        self.enbedding_client = embedding_client
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository
        self.column_milvus_repository = column_milvus_repository

    async def build(self, config_path: Path):
        meta_config: MetaConfig = load_config(config_path, MetaConfig)
        if meta_config.tables:
            tables: list[TableInfo] = []
            columns: list[ColumnInfo] = []

            for table in meta_config.tables:
                tables.append(
                    TableInfo(
                        id=table.name,
                        name=table.name,
                        role=table.role,
                        description=table.description,
                    )
                )
                types = await self.dw_mysql_repository.get_column_types(table.name)

                for column in table.columns:
                    values = await self.dw_mysql_repository.get_column_values(
                        table.name, column.name
                    )
                    columns.append(
                        ColumnInfo(
                            id=f"{table.name}.{column.name}",
                            name=column.name,
                            type=types.get(column.name, "unknown"),
                            role=column.role,
                            examples=values,
                            description=column.description,
                            alias=column.alias,
                            table_id=table.name,
                        )
                    )
            # 存储到元数据库
            async with self.meta_mysql_repository.session.begin():
                await self.meta_mysql_repository.save_table_infos(tables)
                await self.meta_mysql_repository.save_column_infos(columns)
            # 对字段信息建立向量索引
            await self.column_milvus_repository.ensure_collection()

            points: list[dict] = []
            for column in columns:
                embedding_texts = [column.name]
                if column.description:
                    embedding_texts.append(column.description)
                if column.alias:
                    embedding_texts.extend(column.alias)

                for text in embedding_texts:
                    points.append(
                        {
                            "id": str(uuid.uuid4()),
                            "embedding_text": text,
                            "payload": Mapper.to_dict(column),
                        }
                    )

            embedding_texts = [point.pop("embedding_text") for point in points]
            embeddings = await self.enbedding_client.embed_batch(embedding_texts)

            datas = [
                {
                    "id": point["id"],
                    "embedding": embedding,
                    "payload": point["payload"],
                }
                for point, embedding in zip(points, embeddings)
            ]

            await self.column_milvus_repository.save_column_embeddings(datas)

            # TODO：对维度字段建全文索引

        if meta_config.metrics:
            # TODO: 同步指标信息
            pass
