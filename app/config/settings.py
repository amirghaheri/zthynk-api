from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "local"

    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int = 5432
    db_driver: str = "postgresql+psycopg"
    callback_url: str = "http://localhost:3130/auth/callback"

    cognito_region: str
    cognito_user_pool_id: str
    cognito_client_id: str
    cognito_client_secret: str
    cognito_domain: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
