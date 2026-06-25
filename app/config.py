from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://rescute:rescute@localhost:5432/rescute"
    SECRET_KEY: str = "dev-secret-key"
    AI_PROVIDER_KEY: str = ""
    AI_MODEL: str = "gemini-2.5-flash-lite"
    AI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def ai_enabled(self) -> bool:
        return bool(self.AI_PROVIDER_KEY)

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
