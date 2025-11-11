# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # This will automatically load environment variables.
    # We define defaults for development.
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "a-very-secret-and-random-key-for-this-poc"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./profiles.db"

    class Config:
        case_sensitive = True


settings = Settings()