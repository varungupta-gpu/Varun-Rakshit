import os
from functools import lru_cache
from pathlib import Path

import yaml

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config.yaml"
)


@lru_cache(maxsize=1)
def get_config() -> dict:
    path = os.path.abspath(CONFIG_PATH)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if cfg is None:
        cfg = {}
    return cfg


def config_value(*keys: str, default=None):
    current = get_config()
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
