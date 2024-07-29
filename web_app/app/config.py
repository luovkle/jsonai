from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvEnum(str, Enum):
    dev = "dev"
    test = "test"
    prod = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(use_enum_values=True)

    APP_SECRET_KEY: str = Field(min_length=64)
    APP_ENV: EnvEnum = EnvEnum.prod

    CACHE_DB_HOST: str
    CACHE_DB_PORT: int = 6379
    CACHE_DB_PASSWORD: str
    CACHE_DB_SSL: bool = True

    DB_URI: str
    DB_NAME: str

    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    OPENAI_MAX_TOKENS: int
    OPENAI_TEMPERATURE: int

    SENTRY_DSN: str
    SENTRY_TRACES_SAMPLE_RATE: float = Field(ge=0, le=1)
    SENTRY_PROFILES_SAMPLE_RATE: float = Field(ge=0, le=1)


settings = Settings()  # type: ignore
