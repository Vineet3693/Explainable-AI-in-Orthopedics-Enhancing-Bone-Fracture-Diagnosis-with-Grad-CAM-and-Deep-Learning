"""
Logging Configuration

PURPOSE:
    Centralized logging configuration for the entire application.
    Sets up formatters, handlers, and log levels.

USAGE:
    from src.monitoring.logging.log_config import setup_logging
    
    setup_logging(level='INFO', log_dir='logs')
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(
    level: str = 'INFO',
    log_dir: str = 'logs',
    app_name: str = 'fracture_detection'
):
    """
    Setup application logging
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        app_name: Application name for log files
    """
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    date_str = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f'{app_name}_{date_str}.log')
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging configured: level={level}, file={log_file}")


__all__ = ['setup_logging']
