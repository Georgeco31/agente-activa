from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Agua Sales API"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "agua_sales"
    postgres_user: str = "agua_user"
    postgres_password: str = "agua_password"
    database_url: str | None = Field(default=None)
    agent_simulation_token: str | None = Field(default=None)
    whatsapp_webhook_enabled: bool = False
    whatsapp_webhook_verify_token: str | None = Field(default=None)
    whatsapp_app_secret: str | None = Field(default=None)

    @cached_property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
