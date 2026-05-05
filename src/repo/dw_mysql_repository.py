from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class DwMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        sql = f"SHOW columns FROM `{table_name}`"
        res = await self.session.execute(text(sql))
        return {row["Field"]: row["Type"] for row in res.mappings().fetchall()}

    async def get_column_values(
        self, table_name: str, column_name: str, limit=10
    ) -> list[str]:
        sql = f"SELECT DISTINCT  `{column_name}` FROM `{table_name}` LIMIT {limit}"
        res = await self.session.execute(text(sql))
        return [row[0] for row in res.fetchall()]
