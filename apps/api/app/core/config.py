from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables de entorno. Los valores por defecto son los del entorno local (`supabase start`)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
    supabase_url: str = "http://127.0.0.1:54321"
    web_origin: str = "http://localhost:3000"

    notificaciones_proveedor: Literal["consola", "whatsapp"] = "consola"
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_app_secret: str = ""
    whatsapp_verify_token: str = ""

    sentry_dsn: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
