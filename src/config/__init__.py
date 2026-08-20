from pathlib import Path

from pydantic_settings import BaseSettings

_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    API_OMIE_BASE: str
    API_KEY_OMIE: str
    API_SECRET_OMIE: str

    class Config:
        env_file = str(_ENV_PATH)
        env_file_encoding = "utf-8"
        extra = "ignore"