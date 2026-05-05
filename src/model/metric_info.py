from typing import TYPE_CHECKING

from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import Base

if TYPE_CHECKING:
    from src.model.column_info import ColumnInfo


class MetricInfo(Base):
    __tablename__ = "metric_info"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="指标编码")
    name: Mapped[str] = mapped_column(String(128), comment="指标名称")
    description: Mapped[str | None] = mapped_column(Text, comment="指标描述")
    relevant_columns: Mapped[dict | None] = mapped_column(JSON, comment="关联的列")
    alias: Mapped[dict | None] = mapped_column(JSON, comment="指标别名")

    columns: Mapped[list["ColumnInfo"]] = relationship(
        "ColumnInfo", secondary="column_metric", back_populates="metrics"
    )
