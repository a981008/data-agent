from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert as mysql_insert
from src.entity.meta_entity import ColumnInfo, TableInfo
from src.model.table_info import TableInfoMySQL
from src.model.column_info import ColumnInfoMySQL

from src.repo.mapper import Mapper


class MetaMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_table_infos(self, tables: list[TableInfo]):
        if not tables:
            return
        values = [Mapper.to_dict(t) for t in tables]
        stmt = mysql_insert(TableInfoMySQL).values(values)
        stmt = stmt.on_duplicate_key_update(TableInfoMySQL.__table__.columns)
        await self.session.execute(stmt)

    async def save_column_infos(self, columns: list[ColumnInfo]):
        if not columns:
            return
        values = [Mapper.to_dict(c) for c in columns]
        stmt = mysql_insert(ColumnInfoMySQL).values(values)
        stmt = stmt.on_duplicate_key_update(ColumnInfoMySQL.__table__.columns)
        await self.session.execute(stmt)
