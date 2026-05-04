from src.conf.config_loader import load_config
from src.conf.meta_config import MetaConfig, TableConfig, ColumnConfig, MetricConfig


class TestMetaConfig:
    def test_meta_config_with_tables_and_columns(self, tmp_path):
        yaml_content = """
tables:
  - name: users
    role: dimension
    description: User dimension table
    columns:
      - name: id
        role: primary_key
        description: User ID
        alias:
          - user_id
          - uid
        sync: true
      - name: name
        role: attribute
        description: User name
        alias:
          - user_name
        sync: false
  - name: orders
    role: fact
    description: Order fact table
    columns:
      - name: order_id
        role: primary_key
        description: Order ID
        alias:
          - o_id
        sync: true
"""
        config_file = tmp_path / "meta_tables.yaml"
        config_file.write_text(yaml_content)

        config = load_config(config_file, MetaConfig)

        assert len(config.tables) == 2
        assert config.tables[0].name == "users"
        assert config.tables[0].role == "dimension"
        assert config.tables[0].columns[0].name == "id"
        assert config.tables[0].columns[0].alias == ["user_id", "uid"]
        assert config.tables[0].columns[0].sync is True
        assert config.tables[1].name == "orders"
        assert config.tables[1].columns[0].sync is True

    def test_meta_config_with_metrics(self, tmp_path):
        yaml_content = """
metrics:
  - name: total_orders
    description: Total number of orders
    relevant_columns:
      - orders.order_id
      - orders.created_at
    alias:
      - order_count
      - total
  - name: revenue
    description: Total revenue
    relevant_columns:
      - orders.amount
    alias:
      - total_revenue
"""
        config_file = tmp_path / "meta_metrics.yaml"
        config_file.write_text(yaml_content)

        config = load_config(config_file, MetaConfig)

        assert len(config.metrics) == 2
        assert config.metrics[0].name == "total_orders"
        assert config.metrics[0].relevant_columns == [
            "orders.order_id",
            "orders.created_at",
        ]
        assert config.metrics[0].alias == ["order_count", "total"]
        assert config.metrics[1].name == "revenue"
        assert config.metrics[1].alias == ["total_revenue"]

    def test_meta_config_empty(self, tmp_path):
        yaml_content = ""
        config_file = tmp_path / "meta_empty.yaml"
        config_file.write_text(yaml_content)

        config = load_config(config_file, MetaConfig)

        assert config.tables == []
        assert config.metrics == []

    def test_meta_config_partial(self, tmp_path):
        yaml_content = """
tables:
  - name: products
    role: dimension
    description: Product dimension
    columns:
      - name: product_id
        role: primary_key
        description: Product ID
        alias:
          - pid
        sync: true
"""
        config_file = tmp_path / "meta_partial.yaml"
        config_file.write_text(yaml_content)

        config = load_config(config_file, MetaConfig)

        assert len(config.tables) == 1
        assert config.tables[0].name == "products"
        assert config.metrics == []
