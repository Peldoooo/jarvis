"""
OpenRouter API Client
Handles AI interactions using OpenRouter API
"""

import requests
import json
from typing import List, Dict, Any, Optional
from config.config import config
from utils.logger import get_logger

class OpenRouterClient:
    """OpenRouter API client for AI interactions"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.api_key = config.get('openrouter.api_key')
        self.base_url = config.get('openrouter.base_url')
        self.model = config.get('openrouter.model')
        self.max_tokens = config.get('openrouter.max_tokens', 1000)
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not found in configuration")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/jarvis-assistant",
            "X-Title": "JARVIS Assistant"
        }
    
    def chat_completion(self, messages: List[Dict[str, str]], language: str = "pt-BR") -> str:
        """Get chat completion from OpenRouter"""
        try:
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": 0.7,
                "stream": False
            }
            
            # Make the API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            else:
                self.logger.error(f"Unexpected API response: {result}")
                return self._get_fallback_response(language)
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {e}")
            return self._get_fallback_response(language)
        
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return self._get_fallback_response(language)
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return self._get_fallback_response(language)
    
    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response when AI is unavailable"""
        fallback_responses = {
            'pt-BR': "Desculpe, estou com dificuldades para processar sua solicitação no momento. Tente novamente em alguns instantes.",
            'en-US': "Sorry, I'm having trouble processing your request right now. Please try again in a moment.",
            'es-ES': "Lo siento, tengo problemas para procesar tu solicitud en este momento. Inténtalo de nuevo en unos momentos.",
            'fr-FR': "Désolé, j'ai des difficultés à traiter votre demande en ce moment. Veuillez réessayer dans quelques instants.",
            'de-DE': "Entschuldigung, ich habe gerade Schwierigkeiten, Ihre Anfrage zu bearbeiten. Versuchen Sie es in einem Moment noch einmal."
        }
        
        return fallback_responses.get(language, fallback_responses['en-US'])
    
    def test_connection(self) -> bool:
        """Test the API connection"""
        try:
            test_messages = [{
                "role": "user",
                "content": "Hello, can you hear me?"
            }]
            
            response = self.chat_completion(test_messages, "en-US")
            return bool(response and len(response) > 0)
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'data' in result:
                return [model['id'] for model in result['data']]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting models: {e}")
            return []
