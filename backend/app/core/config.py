from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"

    ENABLE_VERTEX: bool = False
    VERTEX_PROJECT: str | None = None
    VERTEX_LOCATION: str | None = None
    VERTEX_MODEL_NAME: str | None = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    def vertex_enabled(self) -> bool:
        return (
            self.ENABLE_VERTEX
            and self.VERTEX_PROJECT
            and self.VERTEX_LOCATION
            and self.VERTEX_MODEL_NAME
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()
