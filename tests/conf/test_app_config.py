from src.conf.app_config import app_config


class TestAppConfig:
    def test_load_app_config_from_file(self):
        assert app_config.db_meta.host == "localhost"
        assert app_config.db_meta.port == 3306
        assert app_config.db_dw.database == "dw"
        assert app_config.qdrant.embedding_size == 1024
        assert app_config.embedding.model == "BAAI/bge-large-zh-v1.5"
        assert app_config.es.index_name == "data_agent"
        assert app_config.llm.model_name == "gpt-5.2-codex"
        assert app_config.logging.file.enable is True
        assert app_config.logging.console.level == "INFO"
        assert app_config.db_meta.password == "!QAZ2wsx123"
