from typing import TYPE_CHECKING

from sqlalchemy import String, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import Base

if TYPE_CHECKING:
    from src.model.table_info import TableInfo
    from src.model.metric_info import MetricInfo


class ColumnInfo(Base):
    __tablename__ = "column_info"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="列编号")
    name: Mapped[str] = mapped_column(String(128), comment="列名称")
    type: Mapped[str] = mapped_column(String(64), comment="数据类型")
    role: Mapped[str] = mapped_column(String(32), comment="列类型")
    examples: Mapped[dict | None] = mapped_column(JSON, comment="数据示例")
    description: Mapped[str | None] = mapped_column(Text, comment="列描述")
    alias: Mapped[dict | None] = mapped_column(JSON, comment="列别名")
    table_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("table_info.id"), comment="所属表编号"
    )

    table: Mapped["TableInfo"] = relationship(
        "TableInfo", back_populates="columns"
    )
    metrics: Mapped[list["MetricInfo"]] = relationship(
        "MetricInfo", secondary="column_metric", back_populates="columns"
    )
