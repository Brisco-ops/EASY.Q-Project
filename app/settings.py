from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MenuMVP"
    env: str = "dev"
    base_url: str = "http://localhost:8040"

    database_url: str = "sqlite:///./menu_mvp.db"

    google_api_key: str
    gemini_model: str = "gemini-2.0-flash"

    storage_dir: str = "./storage"
    uploads_dir: str = "./storage/uploads"
    qrs_dir: str = "./storage/qrs"


settings = Settings()
