from pathlib import Path
import json
from src.conf.config_loader import load_config
from src.conf.meta_config import MetaConfig
from src.repo.meta_mysql_repository import MetaMySQLRepository
from src.repo.dw_mysql_repository import DwMySQLRepository
from src.core.log import get_logger
from src.entity.meta_entity import ColumnInfo, TableInfo

logger = get_logger(__name__)


class MetaKnowledgeService:
    def __init__(
        self,
        meta_mysql_repository: MetaMySQLRepository,
        dw_mysql_repository: DwMySQLRepository,
    ):
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository

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

            async with self.meta_mysql_repository.session.begin():
                self.meta_mysql_repository.save_table_infos(tables)
                self.meta_mysql_repository.save_column_infos(columns)

        if meta_config.metrics:
            # TODO: 同步指标信息
            pass
