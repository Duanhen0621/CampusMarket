from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，全部可通过环境变量或 backend/.env 覆盖。"""

    app_name: str = "校园闲置物二手置换平台"
    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "mysql+pymysql://campus:campus@127.0.0.1:3306/campus_market?charset=utf8mb4"
    )

    secret_key: str = "please-change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    upload_dir: str = "static/uploads"
    max_upload_size: int = 5 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
