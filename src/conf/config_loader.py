from pathlib import Path
from typing import Type, cast
import os
import re

from omegaconf import OmegaConf


def _load_env_file(env_path: Path | None = None) -> dict[str, str]:
    """Load environment variables from .env file."""
    if env_path is None:
        env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return {}

    env_vars = {}
    pattern = re.compile(
        r'^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=["\']?([^"\']*)["\']?$'
    )
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = pattern.match(line)
        if m:
            env_vars[m.group(1)] = m.group(2)
    return env_vars


def _preprocess_yaml(yaml_content: str, env_vars: dict[str, str]) -> str:
    """Replace ${VAR} placeholders with environment variable values."""

    def replacer(m: re.Match) -> str:
        var_name = m.group(1)
        value = env_vars.get(var_name, m.group(0))
        return f"'{value}'"

    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", replacer, yaml_content)


def load_config[T](config_file: Path, schema_cls: Type[T]) -> T:
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    env_vars = _load_env_file()
    for key, value in env_vars.items():
        os.environ.setdefault(key, value)

    yaml_text = config_file.read_text(encoding="utf-8")
    yaml_text = _preprocess_yaml(yaml_text, env_vars)

    try:
        context = OmegaConf.create(yaml_text)
    except Exception as e:
        raise ValueError(f"Failed to parse config file: {e}") from e
    schema = OmegaConf.structured(schema_cls)
    config = OmegaConf.to_object(OmegaConf.merge(schema, context))
    return cast(T, config)
