from loguru import logger
import sys
from config.settings import settings

def setup_logger():
    """Configure logging for the application."""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        format="<level>{time:YYYY-MM-DD HH:mm:ss}</level> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL
    )
    
    # Add file handler
    logger.add(
        settings.LOGS_DIR / settings.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="500 MB",
        retention="10 days"
    )
    
    return logger

logger = setup_logger()
