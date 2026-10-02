from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr

class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ADMIN_EMAIL: EmailStr
    ADMIN_PASSWORD: str
    PAYMENT_SUCCESS_RATE: int = 70

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
