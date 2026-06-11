from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cardapio WhatsApp Template"
    environment: str = "development"
    database_url: str = "sqlite:///./data/app.db"

    whatsapp_verify_token: str = "troque_este_token"
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_graph_api_version: str = "v23.0"

    restaurant_name: str = "Sabor Brasileiro"
    restaurant_whatsapp_number: str = "5511999999999"
    restaurant_staff_whatsapp_number: str = "5511999999999"
    delivery_fee: float = 5.0

    public_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
