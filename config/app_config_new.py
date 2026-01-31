"""
Configuration management for the LTM application.
Centralizes all configuration options and provides validation.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    mongodb_uri: str = field(default_factory=lambda: os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
    database_name: str = field(default_factory=lambda: os.getenv("DATABASE_NAME", "ltm_database"))
    collection_name: str = "memories"
    
    def validate(self) -> bool:
        """Validate database configuration."""
        if not self.mongodb_uri:
            logger.error("MongoDB URI is not configured")
            return False
        return True

@dataclass
class ModelConfig:
    """Model configuration settings."""
    provider: str = field(default_factory=lambda: os.getenv("MODEL_PROVIDER", "groq"))
    model_name: str = field(default_factory=lambda: os.getenv("MODEL_NAME", "llama3-70b-8192"))
    ollama_host: str = field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3"))
    
    def validate(self) -> bool:
        """Validate model configuration."""
        if self.provider not in ["groq", "ollama", "openai", "anthropic"]:
            logger.error(f"Invalid model provider: {self.provider}")
            return False
        return True

@dataclass
class EmbeddingConfig:
    """Embedding configuration settings."""
    provider: str = field(default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "openai"))
    model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"))
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions based on model."""
        model_dims = {
            "text-embedding-ada-002": 1536,
            "models/embedding-001": 768,
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768
        }
        return model_dims.get(self.model, 384)

@dataclass
class CrisisDetectionConfig:
    """Crisis detection configuration settings."""
    # Thresholds
    crisis_threshold: float = field(default_factory=lambda: float(os.getenv("CRISIS_THRESHOLD", "0.7")))
    selfie_request_mood_threshold: float = field(default_factory=lambda: float(os.getenv("SELFIE_REQUEST_MOOD_THRESHOLD", "0.6")))
    
    # Timing
    selfie_request_interval_hours: int = field(default_factory=lambda: int(os.getenv("SELFIE_REQUEST_INTERVAL_HOURS", "24")))
    selfie_random_chance: float = field(default_factory=lambda: float(os.getenv("SELFIE_RANDOM_CHANCE", "0.1")))
    
    # Weighting
    negative_word_weight: float = field(default_factory=lambda: float(os.getenv("NEGATIVE_WORD_WEIGHT", "1.0")))
    positive_word_weight: float = field(default_factory=lambda: float(os.getenv("POSITIVE_WORD_WEIGHT", "1.0")))
    pattern_match_weight: float = field(default_factory=lambda: float(os.getenv("PATTERN_MATCH_WEIGHT", "2.0")))
    contextual_indicator_weight: float = field(default_factory=lambda: float(os.getenv("CONTEXTUAL_INDICATOR_WEIGHT", "1.5")))

@dataclass
class IntegrationConfig:
    """Integration configuration settings."""
    # WhatsApp
    whatsapp_api_url: str = field(default_factory=lambda: os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v18.0"))
    whatsapp_access_token: Optional[str] = field(default_factory=lambda: os.getenv("WHATSAPP_ACCESS_TOKEN"))
    whatsapp_phone_number_id: Optional[str] = field(default_factory=lambda: os.getenv("WHATSAPP_PHONE_NUMBER_ID"))
    
    # Telegram
    telegram_bot_token: Optional[str] = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN"))
    
    # EHR
    ehr_api_url: Optional[str] = field(default_factory=lambda: os.getenv("EHR_API_URL"))
    ehr_api_key: Optional[str] = field(default_factory=lambda: os.getenv("EHR_API_KEY"))
    
    # Notification channels
    notification_channels: List[str] = field(default_factory=lambda: os.getenv("NOTIFICATION_CHANNELS", "console,email").split(","))
    critical_alert_contacts: List[str] = field(default_factory=lambda: os.getenv("CRITICAL_ALERT_CONTACTS", "guardian,parent,crisis_hotline").split(","))

@dataclass
class MediaConfig:
    """Media and live session configuration settings."""
    # Audio settings
    audio_format: str = "paInt16"
    channels: int = 1
    send_sample_rate: int = 16000
    receive_sample_rate: int = 24000
    chunk_size: int = 1024
    
    # Live session settings
    live_session_enabled: bool = field(default_factory=lambda: os.getenv("LIVE_SESSION_ENABLED", "false").lower() == "true")
    default_live_mode: str = field(default_factory=lambda: os.getenv("DEFAULT_LIVE_MODE", "camera"))
    
    # Visual context settings
    enable_visual_context: bool = field(default_factory=lambda: os.getenv("ENABLE_VISUAL_CONTEXT", "true").lower() == "true")
    visual_analysis_enabled: bool = field(default_factory=lambda: os.getenv("VISUAL_ANALYSIS_ENABLED", "true").lower() == "true")

@dataclass
class MemoryConfig:
    """Memory management configuration settings."""
    retention_days: int = field(default_factory=lambda: int(os.getenv("MEMORY_RETENTION_DAYS", "365")))
    max_entries: int = field(default_factory=lambda: int(os.getenv("MAX_MEMORY_ENTRIES", "1000")))

@dataclass
class AppConfig:
    """Main application configuration."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    crisis_detection: CrisisDetectionConfig = field(default_factory=CrisisDetectionConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    media: MediaConfig = field(default_factory=MediaConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    
    # API Keys
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    groq_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    google_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    gemini_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    
    # Security
    enable_security_logging: bool = field(default_factory=lambda: os.getenv("ENABLE_SECURITY_LOGGING", "true").lower() == "true")
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> bool:
        """Validate all configuration sections."""
        validations = [
            self.database.validate(),
            self.model.validate()
        ]
        
        if not all(validations):
            logger.error("Configuration validation failed")
            return False
        
        logger.info("Configuration validated successfully")
        return True

# Global configuration instance
_config: Optional[AppConfig] = None

def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config

def reload_config() -> AppConfig:
    """Reload the configuration from environment variables."""
    global _config
    _config = AppConfig()
    return _config