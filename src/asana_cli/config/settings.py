"""Settings management using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="ASANA_",
        env_file=".env",
        extra="ignore",
    )

    token: str | None = None
    workspace: str | None = None
    default_project: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_token() -> str | None:
    """Get the Asana API token from settings or config file."""
    from asana_cli.config.storage import load_config

    # First try environment variable via settings
    settings = get_settings()
    if settings.token:
        return settings.token

    # Then try config file
    config = load_config()
    return config.get("token")


def get_workspace() -> str | None:
    """Get the default workspace from settings or config file."""
    from asana_cli.config.storage import load_config

    # First try environment variable via settings
    settings = get_settings()
    if settings.workspace:
        return settings.workspace

    # Then try config file
    config = load_config()
    return config.get("workspace")
