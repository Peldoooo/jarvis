"""
JARVIS Assistant Package
Main package initialization
"""

__version__ = "1.0.0"
__author__ = "MiniMax Agent"
__description__ = "JARVIS - Just A Rather Very Intelligent System"
__license__ = "MIT"

# Package exports
from .core.jarvis_core import JarvisCore
from .config.config import config

__all__ = [
    'JarvisCore',
    'config',
    '__version__',
    '__author__',
    '__description__',
    '__license__'
]
