import os
from typing import Dict, List, Any
from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    MODELS_DIR = PROJECT_ROOT / "models"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # API Configuration
    WIKIPEDIA_API_TIMEOUT: int = 10
    WIKIDATA_API_TIMEOUT: int = 10
    GITHUB_API_TIMEOUT: int = 10
    PUBMED_API_TIMEOUT: int = 10
    
    # Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    DEVICE: str = "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu"
    
    # Detection Configuration
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.75
    CONTRADICTION_THRESHOLD: float = 0.85
    CONFIDENCE_THRESHOLD: float = 0.7
    MAX_CLAIMS_PER_TEXT: int = 50
    
    # Verification Configuration
    ENABLE_WIKIPEDIA_VERIFICATION: bool = True
    ENABLE_API_VERIFICATION: bool = True
    ENABLE_SEMANTIC_VERIFICATION: bool = True
    VERIFICATION_TIMEOUT: int = 30
    MAX_SOURCES_PER_CLAIM: int = 5
    
    # Domain Configuration
    ENABLED_DOMAINS: List[str] = [
        "general",
        "code",
        "medical",
        "legal",
        "technical"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "hallucination_detector.log"
    
    # Cache Configuration
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
