"""Configuration facilitator."""

import os
from pathlib import Path
from typing import Any

import yaml


class Configuration:
    ENV_VAR_PREFIX = "CONFIG__"

    def __init__(self):
        self._config = None
        self._config_path = None
        self._load_config()

    def _find_config_path(self) -> Path:
        config_path_env = os.getenv("CONFIG_PATH")
        if config_path_env:
            config_path = Path(config_path_env)
            if config_path.is_file():
                return config_path

        # Fall back to current working directory
        cwd_config_path = Path.cwd() / "conf.yml"
        if cwd_config_path.is_file():
            return cwd_config_path

        raise FileNotFoundError("Configuration file not found. Has CONFIG_PATH variable been set?")

    def _load_config(self) -> None:
        self._config_path = self._find_config_path()
        with self._config_path.open("r") as file:
            self._config = yaml.safe_load(file) or {}
        self._load_config_from_environment()

    def _load_config_from_environment(self) -> dict[str, Any]:
        # Load .env file, if present.
        # Note this overrides existing environment variables.
        dotenv_path = Path.cwd() / ".env"
        if dotenv_path.is_file():
            from dotenv import load_dotenv

            load_dotenv(dotenv_path=dotenv_path, override=True)

        # Insert environment variables with prefix self.ENV_VAR_PREFIX.
        # Converts nested keys using double underscore '__' as delimiter.
        for key, value in os.environ.items():
            if key.startswith(self.ENV_VAR_PREFIX):
                config_keys = key[len(self.ENV_VAR_PREFIX) :].lower()
                *path_keys, last_key = config_keys.split("__")
                config = self._config
                for k in path_keys:
                    config = config.setdefault(k, {})
                config[last_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        current = self._config

        try:
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
        except (KeyError, TypeError):
            return default
        else:
            return current

    def reload(self) -> None:
        self._load_config()

    def exists(self, key: str) -> bool:
        return self.get(key) is not None


conf = Configuration()
