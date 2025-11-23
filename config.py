# config.py

import json
import os
from typing import Any, Dict


_CONFIG_CACHE: Dict[str, Any] = {}


def _load_config_file() -> Dict[str, Any]:
    """Load configuration from CONFIG_PATH or config.json if it exists."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE:
        return _CONFIG_CACHE

    config_path = os.getenv("CONFIG_PATH", "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as config_file:
            _CONFIG_CACHE = json.load(config_file)
    else:
        _CONFIG_CACHE = {}
    return _CONFIG_CACHE


def _get_config_value(key: str, default: Any = None) -> Any:
    return os.getenv(key, _load_config_file().get(key, default))


TELEGRAM_BOT_API_TOKEN = _get_config_value("TELEGRAM_BOT_API_TOKEN")
GROUP_CHAT_ID = int(_get_config_value("GROUP_CHAT_ID", 0))

DB_CONFIG = {
    "host": _get_config_value("DB_HOST", "db"),
    "port": int(_get_config_value("DB_PORT", 5432)),
    "dbname": _get_config_value("DB_NAME", "pera_bot_db"),
    "user": _get_config_value("DB_USER", "pera_user"),
    "password": _get_config_value("DB_PASSWORD", ""),
}

