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

    # Telephony Provider
    telephony_provider: str = "twilio"  # "twilio" or "sipgate"

    # Twilio Configuration
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None

    # Sipgate Configuration
    sipgate_email: Optional[str] = None
    sipgate_password: Optional[str] = None
    sipgate_token_id: Optional[str] = None
    sipgate_token: Optional[str] = None
    sipgate_phone_number: Optional[str] = None
    sipgate_device_id: Optional[str] = None  # Device ID (e.g. 'y0') - auto-detected if not provided

    # AI Provider
    ai_provider: str = "anthropic"  # "anthropic" or "openai"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"

    # Speech Services
    deepgram_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_agent_id: Optional[str] = None
    use_elevenlabs_conversational: bool = False  # Use ElevenLabs Conversational AI instead of traditional flow

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

    # Notion Integration
    notion_api_key: Optional[str] = None
    notion_database_id: Optional[str] = None
    notion_enabled: bool = False

    # n8n Webhook Integration
    n8n_webhook_url: Optional[str] = None
    n8n_enabled: bool = False

    def validate_api_keys(self) -> bool:
        """Validate that required API keys are present"""
        # Validate AI provider
        if self.ai_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when AI_PROVIDER is 'anthropic'")
        if self.ai_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'")

        # Validate telephony provider
        if self.telephony_provider == "twilio":
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
                raise ValueError("Twilio credentials required when TELEPHONY_PROVIDER is 'twilio'")
        elif self.telephony_provider == "sipgate":
            if not self.sipgate_phone_number:
                raise ValueError("SIPGATE_PHONE_NUMBER is required")
            has_token = self.sipgate_token_id and self.sipgate_token
            has_password = self.sipgate_email and self.sipgate_password
            if not (has_token or has_password):
                raise ValueError("Sipgate credentials required: either (SIPGATE_TOKEN_ID + SIPGATE_TOKEN) or (SIPGATE_EMAIL + SIPGATE_PASSWORD)")

        return True


# Global settings instance
settings = Settings()
