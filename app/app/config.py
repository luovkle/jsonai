from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_SECRET_KEY: str = Field(min_length=64)

    CACHE_DB_HOST: str
    CACHE_DB_PORT: int

    DB_URI: str
    DB_NAME: str

    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    OPENAI_MAX_TOKENS: int
    OPENAI_TEMPERATURE: int


settings = Settings()  # type: ignore
