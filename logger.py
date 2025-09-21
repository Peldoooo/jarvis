"""
Logging Utilities
Configures logging for JARVIS Assistant
"""

import logging
import os
from datetime import datetime
from typing import Optional
import colorama
from colorama import Fore, Back, Style

# Initialize colorama
colorama.init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT
    }
    
    def format(self, record):
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        
        # Add color to logger name
        if 'jarvis' in record.name.lower():
            record.name = f"{Fore.BLUE}{record.name}{Style.RESET_ALL}"
        
        return super().format(record)

def setup_logger(name: str = 'jarvis', level: str = 'INFO') -> logging.Logger:
    """Setup main logger for JARVIS"""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    console_format = ColoredFormatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler for detailed logs
    log_filename = f"logs/jarvis_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    file_format = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Error file handler
    error_filename = f"logs/jarvis_errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.FileHandler(error_filename, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

class JarvisLogHandler(logging.Handler):
    """Custom log handler for JARVIS GUI"""
    
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback
        self.records = []
        self.max_records = 1000
    
    def emit(self, record):
        try:
            # Store record
            self.records.append(record)
            
            # Keep only recent records
            if len(self.records) > self.max_records:
                self.records = self.records[-self.max_records:]
            
            # Call callback if provided
            if self.callback:
                self.callback(record)
                
        except Exception:
            self.handleError(record)
    
    def get_recent_logs(self, count: int = 100) -> list:
        """Get recent log records"""
        return self.records[-count:] if count < len(self.records) else self.records
