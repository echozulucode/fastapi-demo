"""
Application configuration using Pydantic BaseSettings.
All configuration is loaded from environment variables or .env file.
"""
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "FastAPI Intranet Demo"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Security (local JWT – used only when AUTH_MODE=local)
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-use-openssl-rand-hex-32",
        description="Secret key for local JWT signing",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Authentication mode: "local" (HS256 JWT) | "keycloak" (RS256 via JWKS)
    AUTH_MODE: str = "local"

    # Keycloak / OIDC
    KEYCLOAK_URL: str = "http://keycloak:8080"
    KEYCLOAK_REALM: str = "fastapi-demo"
    KEYCLOAK_CLIENT_ID: str = "fastapi-backend"

    # CORS
    BACKEND_CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:3001,http://localhost:5173"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    # LDAP (deprecated – Keycloak handles AD/LDAP federation)
    LDAP_ENABLED: bool = False
    LDAP_SERVER: Optional[str] = None
    LDAP_PORT: int = 389
    LDAP_USE_SSL: bool = False
    LDAP_USE_NTLM: bool = False
    LDAP_BIND_DN: Optional[str] = None
    LDAP_BIND_PASSWORD: Optional[str] = None
    LDAP_SEARCH_BASE: Optional[str] = None
    LDAP_TIMEOUT: int = 10
    LDAP_USER_SEARCH_FILTER: str = "(sAMAccountName={username})"
    LDAP_GROUP_SEARCH_FILTER: str = "(member={user_dn})"
    LDAP_ADMIN_GROUPS: str = ""
    LDAP_ALLOWED_GROUPS: str = ""

    # Email
    SMTP_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: Optional[str] = None

    # First superuser (bootstrapped on startup)
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
