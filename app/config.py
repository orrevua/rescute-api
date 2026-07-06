from pydantic import field_validator
from pydantic_settings import BaseSettings

_INSECURE_SECRET_KEY = "dev-secret-key"
_MIN_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://rescute:rescute@localhost:5432/rescute"
    SECRET_KEY: str
    AI_PROVIDER_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    AI_BASE_URL: str = "https://api.openai.com/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret_key(cls, value: str) -> str:
        if not value or value == _INSECURE_SECRET_KEY:
            raise ValueError("SECRET_KEY must be set to a strong, non-default value")
        if len(value) < _MIN_SECRET_KEY_LENGTH:
            raise ValueError(f"SECRET_KEY must be at least {_MIN_SECRET_KEY_LENGTH} characters")
        return value

    @property
    def ai_enabled(self) -> bool:
        return bool(self.AI_PROVIDER_KEY)

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
