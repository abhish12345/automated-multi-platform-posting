from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Dev.to
    DEVTO_API_KEY: str = ""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""       # channel/group chat ID, e.g. "@mychannel" or "-100xxxxxxxxx"

    # Mastodon
    MASTODON_ACCESS_TOKEN: str = ""
    MASTODON_INSTANCE_URL: str = "https://mastodon.social"

    # Discord (Incoming Webhook)
    DISCORD_WEBHOOK_URL: str = ""    # Full webhook URL from Discord channel settings

    # Pastebin
    PASTEBIN_API_KEY: str = ""       # Developer API key from pastebin.com

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
