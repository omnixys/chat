from __future__ import annotations

from omnixys_config.settings import AppSettings, CoreSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class ChatCoreSettings(CoreSettings):
    internal_api_key: str = ""


class ChatSettings(AppSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    core: ChatCoreSettings = ChatCoreSettings()

    communication_gateway_url: str = "http://localhost:8002"
    communication_gateway_api_key: str = ""
    communication_gateway_timeout: int = 30
    chat_service_api_key: str = ""

    auth_enabled: bool = True

    @property
    def keycloak_issuer(self) -> str:
        return f"{self.keycloak.url.rstrip('/')}/realms/{self.keycloak.realm}"

    @property
    def keycloak_jwks_url(self) -> str:
        return f"{self.keycloak_issuer}/protocol/openid-connect/certs"


settings = ChatSettings()


def validate_production_settings() -> None:
    import os

    if os.getenv("ENVIRONMENT", "development").lower() != "production":
        return
    required = {
        "CHAT_SERVICE_API_KEY": settings.chat_service_api_key,
        "COMMUNICATION_GATEWAY_API_KEY": settings.communication_gateway_api_key,
        "KEYCLOAK_URL": settings.keycloak.url if settings.auth_enabled else "",
        "VALKEY_URL": settings.cache.url,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"Missing required production settings: {', '.join(missing)}")
