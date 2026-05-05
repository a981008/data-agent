import asyncio
from pathlib import Path
from src.core.log import get_logger
import argparse
from src.service.meta_knowledge_service import MetaKnowledgeService
from src.repo.meta_mysql_repository import MetaMySQLRepository
from src.repo.dw_mysql_repository import DwMySQLRepository
from src.client.mysql_client import MySQLClientManager
from src.conf.app_config import app_config
from src.client.milvus_client import MilvusClientManager
from src.client.es_client import ESClientManager
from src.client.embedding_client import EmbeddingClientManager
from src.repo.column_milvus_repository import ColumnMilvusRepository

logger = get_logger(__name__)


async def build(config_path: Path):
    logger.info(f"Loading configuration from {config_path}...")
    async with (
        MySQLClientManager(app_config.db_meta) as meta_mysql_client,
        MySQLClientManager(app_config.db_dw) as dw_mysql_client,
        MilvusClientManager(app_config.milvus) as milvus_client,
        ESClientManager(app_config.es) as es_client,
        EmbeddingClientManager(app_config.embedding) as embedding_client,
    ):
        dw_sf = dw_mysql_client.session()
        meta_sf = meta_mysql_client.session()
        async with dw_sf() as dw_session, meta_sf() as meta_session:
            meta_mysql_repository = MetaMySQLRepository(meta_session)
            dw_mysql_repository = DwMySQLRepository(dw_session)
            column_milvus_repository = ColumnMilvusRepository(
                milvus_client.client(), str(app_config.milvus.embedding_size)
            )

            service = MetaKnowledgeService(
                embedding_client,
                meta_mysql_repository,
                dw_mysql_repository,
                column_milvus_repository,
            )
            await service.build(config_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build meta-knowledge",
        epilog="Example: python build_meta_knowledge.py",
    )

    parser.add_argument(
        "-c",
        "--conf",
        type=str,
        default="conf/meta_config.yaml",
        help="Path to the config file",
    )
    args = parser.parse_args()

    asyncio.run(build(Path(args.conf)))
