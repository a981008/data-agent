import asyncio
from pathlib import Path
from src.core.log import get_logger
import argparse
from src.service.meta_knowledge_service import MetaKnowledgeService
from src.repo.meta_mysql_repository import MetaMySQLRepository
from src.repo.dw_mysql_repository import DwMySQLRepository
from src.client.mysql_client import MySQLClientManager
from src.conf.app_config import app_config

logger = get_logger(__name__)


async def build(config_path: Path):
    logger.info(f"Loading configuration from {config_path}...")
    async with (
        MySQLClientManager(app_config.db_meta) as meta_mysql_client,
        MySQLClientManager(app_config.db_dw) as dw_mysql_client,
    ):
        dw_sf = dw_mysql_client.session()
        meta_sf = meta_mysql_client.session()
        async with dw_sf() as dw_session, meta_sf() as meta_session:
            meta_mysql_repository = MetaMySQLRepository(meta_session)
            dw_mysql_repository = DwMySQLRepository(dw_session)
            service = MetaKnowledgeService(meta_mysql_repository, dw_mysql_repository)
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
