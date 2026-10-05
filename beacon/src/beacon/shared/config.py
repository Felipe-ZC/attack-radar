from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env"), env_file_encoding="utf-8", extra="ignore"
    )
    # DB Connection Details
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""

    # API
    # Only needed when the UI is served from a different origin than the API
    # (in docker the UI proxies /api, so requests are same-origin). Set as a
    # JSON list, e.g. CORS_ORIGINS='["https://radar.example.com"]'.
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Data Ingestion
    IPDB_API_KEY: str = ""
    DATA_SOURCES_PATH: str = "./data_sources.yaml"


settings = Settings()
