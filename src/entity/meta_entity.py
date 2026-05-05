from dataclasses import dataclass


@dataclass
class ColumnInfo:
    id: str
    name: str
    type: str
    role: str
    examples: list[str]
    description: str
    alias: list[str]
    table_id: str


@dataclass
class ColumnMetric:
    column_id: str
    metric_id: str


@dataclass
class MetricInfo:
    id: str
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


@dataclass
class TableInfo:
    id: str
    name: str
    role: str
    description: str | None


@dataclass
class ValueInfo:
    id: str
    value: str
    column_id: str
