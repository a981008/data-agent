from dataclasses import dataclass, field
from typing import List


@dataclass
class ColumnConfig:
    name: str
    role: str
    description: str
    alias: List[str]
    sync: bool


@dataclass
class TableConfig:
    name: str
    role: str
    description: str
    columns: List[ColumnConfig]


@dataclass
class MetricConfig:
    name: str
    description: str
    relevant_columns: List[str]
    alias: List[str]


@dataclass
class MetaConfig:
    tables: List[TableConfig] = field(default_factory=list)
    metrics: List[MetricConfig] = field(default_factory=list)
