from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI VolleyPRO"
    debug: bool = True
    environment: str = "development"

    # SECURITY
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    security_bcrypt_rounds: int = 12
    security_argon2_time_cost: int = 2
    security_argon2_memory_cost: int = 102400
    security_argon2_parallelism: int = 2

    # POSTGRESQL
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fastapi_pay"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # CORS
    cors_origins: list[str] = ["*"]

    # STATIC
    static_dir: str = "static"
    images_dir: str = "static/images"

    # REDIS
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # EMAIL
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    WELCOME_EMAIL_SUBJECT: str = "Добро пожаловать в FastAPI VolleyPRO"

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensetive=False,
        extra="ignore",
    )


settings = Settings()
