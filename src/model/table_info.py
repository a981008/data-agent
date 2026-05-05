from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import Base

if TYPE_CHECKING:
    from src.model.column_info import ColumnInfo


class TableInfo(Base):
    __tablename__ = "table_info"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="表编号")
    name: Mapped[str] = mapped_column(String(128), comment="表名称")
    role: Mapped[str] = mapped_column(String(32), comment="表类型(fact/dim)")
    description: Mapped[str | None] = mapped_column(Text, comment="表描述")

    columns: Mapped[list["ColumnInfo"]] = relationship(
        "ColumnInfo", back_populates="table", lazy="selectin"
    )
