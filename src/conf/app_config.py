from dataclasses import dataclass
from pathlib import Path

from src.conf.config_loader import load_config


# 日志配置
@dataclass
class File:
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str


@dataclass
class Console:
    enable: bool
    level: str


@dataclass
class LoggingConfig:
    file: File
    console: Console


# 数据库配置
@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class MilvusConfig:
    host: str
    port: int
    embedding_size: int


@dataclass
class EmbeddingConfig:
    host: str
    port: int
    model: str


@dataclass
class ESConfig:
    host: str
    port: int
    index_name: str


@dataclass
class LLMConfig:
    model_name: str
    api_key: str
    base_url: str


@dataclass
class AppConfig:
    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    milvus: MilvusConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig


config_path = Path(__file__).parents[2] / "conf" / "app_config.yaml"

try:
    app_config: AppConfig = load_config(config_path, AppConfig)
except Exception as e:
    raise RuntimeError(f"Failed to load app_config from {config_path}: {e}") from e
