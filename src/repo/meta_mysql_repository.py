from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from src.entity.meta_entity import ColumnInfo, TableInfo
from src.model.table_info import TableInfoMySQL
from src.model.column_info import ColumnInfoMySQL

from src.repo.mapper import Mapper


class MetaMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def save_table_infos(self, tables: list[TableInfo]):
        for table in tables:
            self.session.add(Mapper.to_model(table, TableInfoMySQL))

    def save_column_infos(self, columns: list[ColumnInfo]):
        for column in columns:
            self.session.add(Mapper.to_model(column, ColumnInfoMySQL))
