from json import load
from typing import Dict, Any

from core.settings import settings

class TextsError(Exception):
    ...

class Texts():
    def __init__(self, texts_path: str) -> None:
        try:
            with open(texts_path, "r", encoding="utf-8") as json_texts:
                for key, value in load(json_texts).items():
                    setattr(self, key, value)
        except Exception:
            raise TextsError(f"Texts file at {texts_path} is invalid or not found")

    def get_command_descriptions(self, command: str) -> Dict[str, str]:
        try:
            return getattr(self, "COMMAND_DESCRIPTIONS").get(command)
        except Exception:
            raise TextsError(f"Localization for command {command} is invalid or not found")
    
    def get_embed_data(self, embed: str) -> Dict[str, Any]:
        try:
            return getattr(self, "EMBED_MESSAGES").get(embed)
        except Exception:
            raise TextsError(f"Embed message {embed} is invalid or not found")
    
    def get_error_text(self, error: str) -> str:
        try:
            return getattr(self, "ERRORS").get(error)
        except:
            raise TextsError(f"Error message {error} is invalid or not found")
    
    def get_message_text(self, message: str) -> str:
        try:
            return getattr(self, "SIMPLE_MESSAGES").get(message)
        except:
            raise TextsError(f"Simple message {message} is invalid or not found")

texts = Texts(settings.get_config("TEXTS_PATH"))