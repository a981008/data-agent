from src.conf.config_loader import load_config
from src.conf.app_config import AppConfig


class TestConfigLoader:
    def test_load_config_with_valid_yaml(self, tmp_path):
        yaml_content = """
db_meta:
  host: localhost
  port: 3306
  user: test_user
  password: test_pass
  database: test_db
db_dw:
  host: localhost
  port: 3306
  user: test_user
  password: test_pass
  database: test_dw
qdrant:
  host: localhost
  port: 6333
  embedding_size: 1024
embedding:
  host: localhost
  port: 8081
  model: test-model
es:
  host: localhost
  port: 9200
  index_name: test_index
llm:
  model_name: gpt-4
  api_key: test-key
  base_url: https://api.test.com
logging:
  file:
    enable: false
    level: DEBUG
    path: logs
    rotation: 10 MB
    retention: 7 days
  console:
    enable: true
    level: INFO
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(yaml_content)

        config = load_config(config_file, AppConfig)

        assert config.db_meta.host == "localhost"
        assert config.db_meta.port == 3306
        assert config.db_meta.user == "test_user"
        assert config.db_dw.database == "test_dw"
        assert config.qdrant.embedding_size == 1024
        assert config.embedding.model == "test-model"
        assert config.es.index_name == "test_index"
        assert config.llm.model_name == "gpt-4"
        assert config.logging.console.level == "INFO"

    def test_load_config_with_defaults(self, tmp_path):
        yaml_content = """
db_meta:
  host: db1
  port: 3307
  user: user1
  password: pass1
  database: db1
db_dw:
  host: db1
  port: 3307
  user: user1
  password: pass1
  database: db2
qdrant:
  host: qdrant.local
  port: 6334
  embedding_size: 512
embedding:
  host: embedding.local
  port: 8082
  model: model-v2
es:
  host: es.local
  port: 9201
  index_name: idx
llm:
  model_name: gpt-5
  api_key: key2
  base_url: https://api.test2.com
logging:
  file:
    enable: true
    level: WARNING
    path: custom_logs
    rotation: 50 MB
    retention: 14 days
  console:
    enable: false
    level: ERROR
"""
        config_file = tmp_path / "test_config2.yaml"
        config_file.write_text(yaml_content)

        config = load_config(config_file, AppConfig)

        assert config.db_meta.host == "db1"
        assert config.db_meta.port == 3307
        assert config.qdrant.host == "qdrant.local"
        assert config.es.port == 9201
        assert config.logging.file.rotation == "50 MB"
