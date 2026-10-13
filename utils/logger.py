import logging
import sys
from config import settings

def setup_logging():
    """
    Configure logging for the application
    
    This sets up logging with appropriate handlers and formatters
    based on the environment (development or production).
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL)
    root_logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # In production, we might add a file handler or other handlers
    if settings.ENV == "production":
        # Example: Add a file handler for production
        # file_handler = logging.FileHandler("/var/log/dmv-muslims/app.log")
        # file_handler.setFormatter(formatter)
        # root_logger.addHandler(file_handler)
        pass
    
    # Set specific log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Return configured logger
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Name of the logger (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)