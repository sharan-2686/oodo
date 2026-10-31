from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Brightloop 360 API"
    environment: str = "development"
    database_url: str = "mysql+pymysql://brightloop_app:change-me@localhost:3306/brightloop360?charset=utf8mb4"
    sql_echo: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
