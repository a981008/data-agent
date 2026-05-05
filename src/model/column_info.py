from typing import TYPE_CHECKING

from sqlalchemy import String, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from src.model.base import Base

if TYPE_CHECKING:
    from src.model.table_info import TableInfoMySQL
    from src.model.metric_info import MetricInfoMySQL


class EmptyListOrStr(TypeDecorator):
    impl = JSON
    cache_ok = True

    def process_result_value(self, value, _dialect):
        if value is None:
            return []
        return value


class ColumnInfoMySQL(Base):
    __tablename__ = "column_info"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="列编号")
    name: Mapped[str] = mapped_column(String(128), comment="列名称")
    type: Mapped[str] = mapped_column(String(64), comment="数据类型")
    role: Mapped[str] = mapped_column(String(32), comment="列类型")
    examples: Mapped[list[str]] = mapped_column(EmptyListOrStr(), comment="数据示例")
    description: Mapped[str] = mapped_column(Text, nullable=True, default="", comment="列描述")
    alias: Mapped[list[str]] = mapped_column(EmptyListOrStr(), comment="列别名")
    table_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("table_info.id"), nullable=True, comment="所属表编号"
    )

    table: Mapped["TableInfoMySQL"] = relationship(
        "TableInfoMySQL", back_populates="columns"
    )
    metrics: Mapped[list["MetricInfoMySQL"]] = relationship(
        "MetricInfoMySQL", secondary="column_metric", back_populates="columns"
    )

    def __repr__(self):
        return f"<ColumnInfoMySQL(id={self.id!r}, name={self.name!r})>"
