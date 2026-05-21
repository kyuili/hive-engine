"""
HiveEngine Configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for HiveEngine."""
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    
    # API Keys
    MIMO_API_KEY: str = os.getenv("MIMO_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Data
    DATA_DIR: str = os.getenv("DATA_DIR", ".hiveengine")
    
    # Rate Limiting
    MAX_CONCURRENT_SCANS: int = int(os.getenv("MAX_CONCURRENT_SCANS", "10"))
    MAX_TOKENS_PER_SCAN: int = int(os.getenv("MAX_TOKENS_PER_SCAN", "50000"))
    
    # Agent Configuration
    AGENT_TIMEOUT: int = 60  # seconds
    MAX_RETRIES: int = 3
    
    # Model Configuration
    DEFAULT_MODELS = {
        "security": "mimo-v2.5-pro",
        "quality": "claude-sonnet",
        "logic": "gpt-4-turbo",
        "deps": "mimo-v2.5-pro",
        "secrets": "claude-haiku"
    }
    
    @classmethod
    def get_data_path(cls) -> Path:
        """Get the data directory path."""
        path = Path(cls.DATA_DIR)
        path.mkdir(exist_ok=True)
        return path


# Global config instance
config = Config()
