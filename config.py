"""
JARVIS Configuration Module
Handles all configuration settings and API keys
"""

import os
from dotenv import load_dotenv
import json
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config:
    """Configuration management class"""
    
    def __init__(self):
        self.load_default_config()
        self.load_user_config()
    
    def load_default_config(self):
        """Load default configuration"""
        self.config = {
            # API Configuration
            "openrouter": {
                "api_key": os.getenv("OPENROUTER_API_KEY", ""),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "anthropic/claude-3-sonnet",
                "max_tokens": 1000
            },
            
            # Voice Configuration
            "voice": {
                "engine": "pyttsx3",  # pyttsx3, gtts
                "rate": 150,
                "volume": 0.8,
                "voice_id": 0,  # 0 for male, 1 for female
                "language": "pt-br"
            },
            
            # Speech Recognition
            "speech": {
                "language": "pt-BR",
                "timeout": 5,
                "phrase_timeout": 1,
                "energy_threshold": 300
            },
            
            # Camera Configuration
            "camera": {
                "device_id": 0,
                "width": 640,
                "height": 480,
                "fps": 30
            },
            
            # UI Configuration
            "ui": {
                "theme": "dark",
                "accent_color": "#00D4FF",
                "background_color": "#0A0A0A",
                "text_color": "#FFFFFF",
                "window_size": "1200x800",
                "transparency": 0.95
            },
            
            # Languages
            "languages": {
                "supported": ["pt-BR", "en-US", "es-ES", "fr-FR", "de-DE"],
                "default": "pt-BR"
            },
            
            # Features
            "features": {
                "voice_activation": True,
                "wake_word": "jarvis",
                "auto_listen": True,
                "face_recognition": False,
                "gesture_control": False,
                "home_automation": False
            }
        }
    
    def load_user_config(self):
        """Load user-specific configuration"""
        config_file = "config/user_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.merge_config(user_config)
            except Exception as e:
                print(f"Error loading user config: {e}")
    
    def merge_config(self, user_config: Dict[str, Any]):
        """Merge user configuration with default configuration"""
        def deep_merge(default: dict, user: dict) -> dict:
            for key, value in user.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    deep_merge(default[key], value)
                else:
                    default[key] = value
            return default
        
        self.config = deep_merge(self.config, user_config)
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_user_config(self):
        """Save current configuration to user config file"""
        os.makedirs("config", exist_ok=True)
        
        with open("config/user_config.json", 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

# Global configuration instance
config = Config()
