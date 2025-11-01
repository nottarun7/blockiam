"""
Logging configuration for iot_iam library
"""

import logging
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


def setup_logger(
    name: str = "iot_iam",
    level: int = logging.INFO,
    use_rich: bool = True
) -> logging.Logger:
    """
    Setup logger with optional Rich formatting
    
    Args:
        name: Logger name
        level: Logging level
        use_rich: Use Rich handler for pretty output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    if use_rich:
        handler = RichHandler(
            console=Console(stderr=True),
            show_time=True,
            show_path=False,
            markup=True
        )
        formatter = logging.Formatter(
            "%(message)s",
            datefmt="[%X]"
        )
    else:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Default logger instance
logger = setup_logger()
