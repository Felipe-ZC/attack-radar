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

    # Data Ingestion
    IPDB_API_KEY: str = ""
    DATA_SOURCES_PATH: str = "./data_sources.yaml"


settings = Settings()
