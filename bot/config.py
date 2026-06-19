from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    BOT_TOKEN: str
    BACKEND_URL: str = "http://localhost:8000"
    INTERNAL_API_KEY: str = "internal-api-key-for-bot"

    class Config:
        env_file = ".env"


settings = BotSettings()
