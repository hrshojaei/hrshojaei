"""
Configuration management for the AI Calling Agent
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Twilio Configuration
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    # AI Provider
    ai_provider: str = "anthropic"  # "anthropic" or "openai"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"

    # Speech Services
    deepgram_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"

    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    public_url: str = "http://localhost:8000"

    # Database
    database_url: str = "sqlite:///./data/candidates.db"

    # Company Information
    company_name: str = "Hörakustik Excellence GmbH"
    company_description: str = "Führender Hörakustik-Anbieter mit modernster Technologie"
    job_benefits: str = "Attraktives Gehalt, Firmenwagen, Weiterbildung, flexible Arbeitszeiten"
    contact_email: str = "recruiting@example.com"
    contact_phone: str = "+491234567890"

    # Conversation Settings
    default_language: str = "de-DE"
    max_conversation_turns: int = 20
    call_timeout_seconds: int = 600

    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True

    def validate_api_keys(self) -> bool:
        """Validate that required API keys are present"""
        if self.ai_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when AI_PROVIDER is 'anthropic'")
        if self.ai_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'")
        return True


# Global settings instance
settings = Settings()
