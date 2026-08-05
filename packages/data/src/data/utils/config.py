"""Configuration for the data package."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config import workspace_root

# Root env located at packages/.env
ENV_FILE = workspace_root() / '.env'


class Settings(BaseSettings):
    """MongoDB connection settings from environment."""

    mongodb_uri: str = Field(
        default='mongodb://localhost:27017',
        validation_alias='MONGODB_URI',
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding='utf-8',
        extra='ignore',
    )


settings = Settings()
