import pytest
import uuid
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from src.model.table_info import TableInfo
from src.model.column_info import ColumnInfo
from src.model.metric_info import MetricInfo
from src.model.column_metric import ColumnMetric


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="function")
async def session():
    from src.client.mysql_client import MySQLClientManager
    from src.conf.app_config import app_config

    async with MySQLClientManager(app_config.db_meta) as client:
        sf = client.session()
        async with sf() as s:
            yield s
            # cleanup in dependency order (child first)
            await s.execute(delete(ColumnMetric))
            await s.execute(delete(ColumnInfo))
            await s.execute(delete(MetricInfo))
            await s.execute(delete(TableInfo))
            await s.commit()


class TestTableInfo:
    def test_tablename(self):
        assert TableInfo.__tablename__ == "table_info"

    async def test_insert_and_query(self, session):
        tid = uid("T")
        table = TableInfo(
            id=tid,
            name="fact_order",
            role="fact",
            description="订单事实表",
        )
        session.add(table)
        await session.commit()

        result = await session.execute(select(TableInfo).where(TableInfo.id == tid))
        fetched = result.scalar_one()
        assert fetched.name == "fact_order"
        assert fetched.role == "fact"

    async def test_optional_description(self, session):
        tid = uid("T")
        table = TableInfo(id=tid, name="dim_product", role="dim")
        session.add(table)
        await session.commit()

        result = await session.execute(select(TableInfo).where(TableInfo.id == tid))
        assert result.scalar_one().description is None

    async def test_update(self, session):
        tid = uid("T")
        table = TableInfo(id=tid, name="dim_customer", role="dim", description="原始描述")
        session.add(table)
        await session.commit()

        result = await session.execute(select(TableInfo).where(TableInfo.id == tid))
        fetched = result.scalar_one()
        fetched.description = "更新后的描述"
        await session.commit()

        result = await session.execute(select(TableInfo).where(TableInfo.id == tid))
        assert result.scalar_one().description == "更新后的描述"

    async def test_delete(self, session):
        tid = uid("T")
        table = TableInfo(id=tid, name="dim_region", role="dim")
        session.add(table)
        await session.commit()

        result = await session.execute(select(TableInfo).where(TableInfo.id == tid))
        fetched = result.scalar_one()
        await session.delete(fetched)
        await session.commit()

        result = await session.execute(select(TableInfo).where(TableInfo.id == tid))
        assert result.scalar_one_or_none() is None


class TestColumnInfo:
    def test_tablename(self):
        assert ColumnInfo.__tablename__ == "column_info"

    async def test_insert_and_query(self, session):
        tid = uid("T")
        cid = uid("C")
        table = TableInfo(id=tid, name="fact_order", role="fact")
        col = ColumnInfo(
            id=cid,
            name="order_id",
            type="VARCHAR(30)",
            role="primary_key",
            examples=["ORD001", "ORD002"],
            description="订单编号",
            alias={"zh": "订单ID"},
            table_id=tid,
        )
        session.add_all([table, col])
        await session.commit()

        result = await session.execute(select(ColumnInfo).where(ColumnInfo.id == cid))
        fetched = result.scalar_one()
        assert fetched.name == "order_id"
        assert fetched.examples == ["ORD001", "ORD002"]
        assert fetched.alias == {"zh": "订单ID"}

    async def test_json_fields_null(self, session):
        tid = uid("T")
        cid = uid("C")
        table = TableInfo(id=tid, name="fact_order", role="fact")
        col = ColumnInfo(id=cid, name="amount", type="FLOAT", role="measure", table_id=tid)
        session.add_all([table, col])
        await session.commit()

        result = await session.execute(select(ColumnInfo).where(ColumnInfo.id == cid))
        fetched = result.scalar_one()
        assert fetched.examples is None
        assert fetched.alias is None
        assert fetched.description is None

    async def test_foreign_key_to_table(self, session):
        tid = uid("T")
        cid = uid("C")
        table = TableInfo(id=tid, name="fact_sales", role="fact")
        col = ColumnInfo(id=cid, name="sale_id", type="VARCHAR(30)", role="primary_key", table_id=tid)
        session.add_all([table, col])
        await session.commit()

        result = await session.execute(select(ColumnInfo).where(ColumnInfo.id == cid))
        fetched = result.scalar_one()
        assert fetched.table is not None
        assert fetched.table.name == "fact_sales"


class TestMetricInfo:
    def test_tablename(self):
        assert MetricInfo.__tablename__ == "metric_info"

    async def test_insert_and_query(self, session):
        mid = uid("M")
        metric = MetricInfo(
            id=mid,
            name="total_amount",
            description="总金额",
            relevant_columns=["amount", "quantity"],
            alias={"zh": "总金额"},
        )
        session.add(metric)
        await session.commit()

        result = await session.execute(select(MetricInfo).where(MetricInfo.id == mid))
        fetched = result.scalar_one()
        assert fetched.name == "total_amount"
        assert fetched.relevant_columns == ["amount", "quantity"]

    async def test_optional_fields(self, session):
        mid = uid("M")
        metric = MetricInfo(id=mid, name="order_count")
        session.add(metric)
        await session.commit()

        result = await session.execute(select(MetricInfo).where(MetricInfo.id == mid))
        fetched = result.scalar_one()
        assert fetched.description is None
        assert fetched.relevant_columns is None
        assert fetched.alias is None


class TestColumnMetric:
    def test_tablename(self):
        assert ColumnMetric.__tablename__ == "column_metric"

    async def test_insert_and_query(self, session):
        tid = uid("T")
        cid = uid("C")
        mid = uid("M")
        table = TableInfo(id=tid, name="fact_test", role="fact")
        col = ColumnInfo(id=cid, name="qty", type="INT", role="measure", table_id=tid)
        metric = MetricInfo(id=mid, name="sum_qty")
        cm = ColumnMetric(column_id=cid, metric_id=mid)
        session.add_all([table, col, metric, cm])
        await session.commit()

        result = await session.execute(
            select(ColumnMetric).where(ColumnMetric.column_id == cid, ColumnMetric.metric_id == mid)
        )
        assert result.scalar_one() is not None

    async def test_many_to_many_through_column(self, session):
        tid = uid("T")
        cid = uid("C")
        mid1 = uid("M")
        mid2 = uid("M")
        table = TableInfo(id=tid, name="fact_test", role="fact")
        col = ColumnInfo(id=cid, name="amount", type="FLOAT", role="measure", table_id=tid)
        metric1 = MetricInfo(id=mid1, name="sum_amount")
        metric2 = MetricInfo(id=mid2, name="avg_amount")
        session.add_all([table, col, metric1, metric2])
        await session.commit()

        session.add(ColumnMetric(column_id=cid, metric_id=mid1))
        session.add(ColumnMetric(column_id=cid, metric_id=mid2))
        await session.commit()

        result = await session.execute(
            select(ColumnInfo).options(selectinload(ColumnInfo.metrics)).where(ColumnInfo.id == cid)
        )
        fetched_col = result.scalar_one()
        metric_names = {m.name for m in fetched_col.metrics}
        assert metric_names == {"sum_amount", "avg_amount"}
