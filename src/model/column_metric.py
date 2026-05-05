from sqlalchemy import String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import Base


class ColumnMetricMySQL(Base):
    __tablename__ = "column_metric"
    __table_args__ = (PrimaryKeyConstraint("column_id", "metric_id"),)

    column_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("column_info.id"), primary_key=True, comment="列编号"
    )
    metric_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("metric_info.id"), primary_key=True, comment="指标编号"
    )

    def __repr__(self):
        return f"<ColumnMetricMySQL(column_id={self.column_id!r}, metric_id={self.metric_id!r})>"
