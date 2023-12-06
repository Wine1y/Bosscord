from json import load
from typing import Any


CONFIG_PATH = "config.json"

class ConfigError(Exception):
    ...

class Settings:
    def __init__(self, json_path: str) -> None:
        try:
            with open(json_path, "r", encoding="utf-8") as json_config:
                for key, value in load(json_config).items():
                    setattr(self, key, value)
        except Exception:
            raise ConfigError(f"Config file at {json_path} is invalid or not found")
    
    def get_config(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except Exception:
            raise ConfigError(f"Config variable {key} is invalid or not found")
    
    def get_level_data(self, lvl: int):
        try:
            return self.LVLS[lvl-1]
        except:
            raise ConfigError(f"Level data for lvl {lvl} is invalid or not found")

settings = Settings(CONFIG_PATH)
from core import texts, items