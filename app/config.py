"""Configuration module for Menu Automation pipeline.

Contains environment variable validation, constants, and settings.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Also try loading from parent directory .env if app/.env is missing
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

@dataclass(frozen=True)
class PipelineConfig:
    """Configuration settings for OCR -> AI parsing pipeline."""
    # Environment Variables
    TESSERACT_PATH: str = os.getenv("tesseract") or os.getenv("TESSERACT_PATH", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Gemini Settings
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    TEMPERATURE: float = 0.1
    
    # Chunking Settings
    CHUNK_MIN_CHARS: int = 8000
    CHUNK_MAX_CHARS: int = 10000
    
    # Retry Policy Settings
    MAX_RETRIES: int = 3
    RETRY_INITIAL_DELAY: float = 2.0  # seconds
    RETRY_BACKOFF_FACTOR: float = 2.0
    
    # Description Generation Batching
    DESCRIPTION_BATCH_SIZE: int = 20
    
    # Logs Directory Path
    LOG_DIR: Path = Path(__file__).parent.parent / "logs"

    def validate(self) -> None:
        """Validate required configuration values.

        Raises:
            ValueError: If critical settings or environment variables are missing.
        """
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set in environment or .env file."
            )

        if not self.TESSERACT_PATH:
            raise ValueError(
                "Tesseract executable path is not set (expected 'tesseract' or 'TESSERACT_PATH' in .env)."
            )

        if not os.path.exists(self.TESSERACT_PATH):
            raise ValueError(
                f"Tesseract executable not found at specified path: {self.TESSERACT_PATH}"
            )

# Create singleton instance of configuration
config = PipelineConfig()
