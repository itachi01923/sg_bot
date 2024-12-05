from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    CMC_API_KEY: str
    BOT_TOKEN: str
    ADMIN_ID: str

    @property
    def async_pg_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def get_bot_token(self) -> str:
        return self.BOT_TOKEN

    @property
    def get_admins_id(self) -> list[str]:
        return self.ADMIN_IDS.split(",")

    @property
    def get_debug_mode(self) -> bool:
        return self.DEBUG

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

if settings.get_debug_mode:
    # Время задержки для повторного использования команды (в минутах)
    USER_COOL_DOWN_IN_MINUTE: int = 0
else:
    USER_COOL_DOWN_IN_MINUTE: int = 1

N_DIGITS_DICT: dict[str, list[int]] = {
    "USDT": [0, 0],
    "BTC": [0, 6],
    "LTC": [0, 3]
}
