from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from urllib.parse import quote_plus

from src.conf.app_config import DBConfig
from src.core.log import get_logger

logger = get_logger(__name__)


class MySQLClientManager:
    def __init__(self, config: DBConfig):
        self.config: DBConfig = config
        self._engine = None
        self._session_factory = None

    def _get_url(self) -> str:
        encoded_password = quote_plus(self.config.password)
        return f"mysql+aiomysql://{self.config.user}:{encoded_password}@{self.config.host}:{self.config.port}/{self.config.database}"

    async def connect(self):
        if self._engine is None:
            try:
                self._engine = create_async_engine(
                    self._get_url(), echo=False, pool_pre_ping=True,
                    pool_size=self.config.pool_size, max_overflow=self.config.max_overflow
                )
                self._session_factory = async_sessionmaker(
                    self._engine, expire_on_commit=False
                )
                logger.info(
                    f"MySQL connected to {self.config.host}:{self.config.port}/{self.config.database}"
                )
            except Exception as e:
                logger.exception(f"Failed to connect to MySQL: {e}")
                raise

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self.close()
        return False

    def session(self) -> async_sessionmaker:
        if self._session_factory is not None:
            return self._session_factory
        raise ConnectionError("MySQL client is not connected")

    async def close(self):
        if self._engine is not None:
            engine = self._engine
            session_factory = self._session_factory
            self._engine = None
            self._session_factory = None
            await engine.dispose(close=True)
            logger.info(f"MySQL connection closed: {self.config.database}")


if __name__ == "__main__":
    import asyncio
    from sqlalchemy import select

    async def test_mysql_client():
        from src.conf.app_config import app_config

        # 查询 dw 库的 fact_order 表
        async with MySQLClientManager(app_config.db_dw) as mysql_client:
            sf = mysql_client.session()
            async with sf() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM fact_order"))
                order_count = result.scalar()
                logger.info(f"订单总数: {order_count}")

                # 查询各地区销售汇总
                result = await session.execute(text("""
                    SELECT r.region_name, SUM(f.order_amount) AS total_amount
                    FROM fact_order f
                    JOIN dim_region r ON f.region_id = r.region_id
                    GROUP BY r.region_name
                """))
                for row in result.fetchall():
                    logger.info(f"地区: {row[0]}, 销售总额: {row[1]}")

        # 查询 meta 库的 table_info 表
        async with MySQLClientManager(app_config.db_meta) as mysql_client:
            sf = mysql_client.session()
            async with sf() as session:
                result = await session.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"meta 库中的表: {tables}")

    asyncio.run(test_mysql_client())
