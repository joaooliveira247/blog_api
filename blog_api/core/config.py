from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Blog API"
    API_HOST: str = "localhost"
    API_PORT: int = 5432

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    CACHE_PASSWORD: str
    CACHE_HOST: str
    CACHE_PORT: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_dsn(self) -> str:
        return f"redis://:{self.CACHE_PASSWORD}@{self.CACHE_HOST}:{self.API_PORT}/0"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
