from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/mockready"
    )
    supabase_jwt_secret: str = "changeme"
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "https://mock-ready-inky.vercel.app",
        "https://mock-ready-git-main-dhruvgorasiyas-projects.vercel.app",
    ]
    dev_bypass_auth: bool = False
    dev_bypass_user_id: str = "00000000-0000-0000-0000-000000000001"


settings = Settings()
