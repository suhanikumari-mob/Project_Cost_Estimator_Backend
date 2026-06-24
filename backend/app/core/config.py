from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # GROK_API_KEY: str
    GOOGLE_API_KEY: str
    MODEL_NAME: str = "gemini-flash-lite-latest"
    TEMPERATURE: float = 0.2
    MAX_OUTPUT_TOKENS: int = 8192

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()