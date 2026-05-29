from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_OMIE_BASE: str
    API_KEY_OMIE: str
    API_SECRET_OMIE: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"