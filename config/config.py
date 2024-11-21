from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    CMC_API_KEY: str
    BOT_TOKEN: str
    ADMIN_ID: str

    @property
    def async_pg_db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def get_bot_token(self) -> str:
        return self.BOT_TOKEN

    @property
    def get_admin_id_list(self) -> list[str]:
        return self.ADMIN_IDS.split(",")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
